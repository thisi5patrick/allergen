document.addEventListener('DOMContentLoaded', function() {
    const symptomButtons = document.querySelectorAll('.symptom-button');
    const intensitySelectors = document.getElementById('intensitySelectors');
    const selectedSymptoms = {};

    symptomButtons.forEach(button => {
        button.addEventListener('click', function() {
            const symptom = this.getAttribute('data-symptom');
            const symptomName = this.textContent.trim();

            this.classList.toggle('bg-blue-500');
            this.classList.toggle('text-blue-700');
            this.classList.toggle('text-white');

            if (selectedSymptoms[symptom]) {
                delete selectedSymptoms[symptom];
                document.getElementById(`intensity-${symptom}`).remove();
            } else {
                selectedSymptoms[symptom] = true;

                const intensitySelector = document.createElement('div');
                intensitySelector.id = `intensity-${symptom}`;
                intensitySelector.className = 'space-y-1';

                const title = document.createElement('div');
                title.className = 'text-sm font-medium';
                title.textContent = `${symptomName} Intensity:`;
                intensitySelector.appendChild(title);

                const buttonsContainer = document.createElement('div');
                buttonsContainer.className = 'flex space-x-1';

                for (let i = 1; i <= 10; i++) {
                    const intensityButton = document.createElement('button');
                    intensityButton.className = 'w-7 h-7 rounded-full bg-gray-200 hover:bg-blue-400 text-xs font-medium transition-colors';
                    intensityButton.textContent = i;
                    intensityButton.setAttribute('data-intensity', i);

                    intensityButton.addEventListener('click', function() {
                        buttonsContainer.querySelectorAll('button').forEach(btn => {
                            btn.classList.remove('bg-blue-500', 'text-white');
                            btn.classList.add('bg-gray-200');
                        });

                        this.classList.remove('bg-gray-200');
                        this.classList.add('bg-blue-500', 'text-white');

                        selectedSymptoms[symptom] = parseInt(this.getAttribute('data-intensity'));
                        console.log(selectedSymptoms);
                    });

                    buttonsContainer.appendChild(intensityButton);
                }

                intensitySelector.appendChild(buttonsContainer);
                intensitySelectors.appendChild(intensitySelector);
            }

            if (Object.keys(selectedSymptoms).length > 0) {
                intensitySelectors.classList.remove('hidden');
            } else {
                intensitySelectors.classList.add('hidden');
            }
        });
    });
});
