document.addEventListener("DOMContentLoaded", function() {
    const symptomButtons = document.querySelectorAll('.symptom-button');
    const intensitySelectors = document.getElementById('intensitySelectors');
    const selectedSymptoms = {};

    let currentSelectedDate = getTodayFormatted();

    function getTodayFormatted() {
        const today = new Date();
        return `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    }

    function getCsrfToken() {
        const tokenInput = document.getElementById('csrfToken');
        return tokenInput ? tokenInput.value : '';
    }

    function loadInitialData() {
        const formattedForUrl = currentSelectedDate.replace(/-/g, '/');

        htmx.ajax('GET', `/calendar/${formattedForUrl}/`, {
            target: '#date-info',
            swap: 'innerHTML'
        });
    }

    loadInitialData();

    document.addEventListener('dateSelected', function(e) {
        currentSelectedDate = e.detail.date;
    });

    document.addEventListener('allergy_symptoms_updated', function(e) {
        loadSymptomsFromResponse();
    });

    document.body.addEventListener('htmx:afterSwap', function(e) {
        if (e.detail.target.id === 'date-info') {
            setTimeout(loadSymptomsFromResponse, 50);
        }
    });

    function resetSymptomSelection() {
        Object.keys(selectedSymptoms).forEach(symptom => {
            delete selectedSymptoms[symptom];
        });

        symptomButtons.forEach(button => {
            button.classList.remove('bg-blue-500', 'text-white');
            button.classList.add('bg-blue-50', 'text-blue-700');
        });

        intensitySelectors.innerHTML = '';
        intensitySelectors.classList.add('hidden');
    }

    function loadSymptomsFromResponse() {
        resetSymptomSelection();

        const storedSymptoms = document.querySelectorAll('#stored-symptoms > div');
        let hasSymptoms = false;

        if (storedSymptoms.length > 0) {
            hasSymptoms = true;

            storedSymptoms.forEach(symptomData => {
                const symptom = symptomData.getAttribute('data-symptom');
                const intensity = parseInt(symptomData.getAttribute('data-intensity'), 10);

                symptomButtons.forEach(button => {
                    if (button.getAttribute('data-symptom') === symptom) {
                        button.classList.remove('bg-blue-50', 'text-blue-700');
                        button.classList.add('bg-blue-500', 'text-white');

                        selectedSymptoms[symptom] = true;

                        createIntensitySelector(button, symptom, intensity);
                    }
                });
            });
        } else {
            const symptomElements = document.querySelectorAll('#date-info p');

            symptomElements.forEach(element => {
                const symptomText = element.textContent.trim();
                if (!symptomText || symptomText.includes("No symptoms recorded")) return;

                hasSymptoms = true;
                const parts = symptomText.split(':');
                if (parts.length !== 2) return;

                let displayName = parts[0].trim();
                const intensity = parseInt(parts[1].trim(), 10);

                let symptomEnum;
                if (displayName.toLowerCase().includes("itchy eyes")) symptomEnum = "ITCHY_EYES";
                else if (displayName.toLowerCase().includes("runny nose")) symptomEnum = "RUNNY_NOSE";
                else if (displayName.toLowerCase().includes("sneezing")) symptomEnum = "SNEEZING";
                else if (displayName.toLowerCase().includes("headache")) symptomEnum = "HEADACHE";

                if (!symptomEnum) return;

                symptomButtons.forEach(button => {
                    if (button.getAttribute('data-symptom') === symptomEnum) {
                        button.classList.remove('bg-blue-50', 'text-blue-700');
                        button.classList.add('bg-blue-500', 'text-white');

                        selectedSymptoms[symptomEnum] = true;

                        createIntensitySelector(button, symptomEnum, intensity);
                    }
                });
            });
        }

        if (hasSymptoms) {
            intensitySelectors.classList.remove('hidden');
        }
    }

    function createIntensitySelector(button, symptom, selectedIntensity = null) {
        const symptomName = button.textContent.trim();

        const intensitySelector = document.createElement('div');
        intensitySelector.id = `intensity-${symptom}`;
        intensitySelector.className = 'space-y-1';

        const title = document.createElement('div');
        title.className = 'text-sm font-medium';
        title.textContent = `${symptomName} intensity:`;
        intensitySelector.appendChild(title);

        const buttonsContainer = document.createElement('div');
        buttonsContainer.className = 'flex space-x-1';

        for (let i = 1; i <= 10; i++) {
            const intensityButton = document.createElement('button');
            const isSelected = selectedIntensity === i;

            intensityButton.className = `w-7 h-7 rounded-full ${isSelected ? 'bg-blue-500 text-white' : 'bg-gray-200'} hover:bg-blue-400 text-xs font-medium transition-colors`;
            intensityButton.textContent = i;
            intensityButton.setAttribute('data-intensity', i);

            intensityButton.setAttribute("hx-post", "/add_symptom/");
            intensityButton.setAttribute("hx-target", "#date-info");
            intensityButton.setAttribute("hx-swap", "innerHTML");
            intensityButton.setAttribute(
                "hx-headers",
                JSON.stringify({ "X-CSRFToken": getCsrfToken() })
            );

            intensityButton.addEventListener('htmx:configRequest', function(evt) {
                const hxData = {
                    symptom_type: symptom,
                    intensity: i,
                    date: currentSelectedDate
                };
                Object.assign(evt.detail.parameters, hxData);
            });

            intensityButton.addEventListener('click', function() {
                buttonsContainer.querySelectorAll('button').forEach(btn => {
                    btn.classList.remove('bg-blue-500', 'text-white');
                    btn.classList.add('bg-gray-200');
                });
                this.classList.remove('bg-gray-200');
                this.classList.add('bg-blue-500', 'text-white');
            });

            buttonsContainer.appendChild(intensityButton);
        }
        htmx.process(buttonsContainer);

        intensitySelector.appendChild(buttonsContainer);
        intensitySelectors.appendChild(intensitySelector);

        intensitySelectors.classList.remove('hidden');
    }

    symptomButtons.forEach(button => {
        button.addEventListener('click', function() {
            const symptom = this.getAttribute('data-symptom');

            this.classList.toggle('bg-blue-50');
            this.classList.toggle('bg-blue-500');
            this.classList.toggle('text-blue-700');
            this.classList.toggle('text-white');

            if (selectedSymptoms[symptom]) {
                const deleteRequest = new XMLHttpRequest();
                deleteRequest.open('POST', '/delete_symptom/');
                deleteRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
                deleteRequest.setRequestHeader('X-CSRFToken', getCsrfToken());
                deleteRequest.send(`symptom=${symptom}&date=${currentSelectedDate}`);

                delete selectedSymptoms[symptom];
                document.getElementById(`intensity-${symptom}`)?.remove();
            } else {
                selectedSymptoms[symptom] = true;
                createIntensitySelector(this, symptom);
            }

            if (Object.keys(selectedSymptoms).length > 0) {
                intensitySelectors.classList.remove('hidden');
            } else {
                intensitySelectors.classList.add('hidden');
            }
        });
    });
});
