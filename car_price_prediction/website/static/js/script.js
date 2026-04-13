const API_BASE_URL = '';
const API_PREDICT_URL = '/predict';
const API_BRANDS_URL = '/brands';
const API_MODELS_URL = '/models';

const form = document.getElementById('predictionForm');
const predictBtn = document.getElementById('predictBtn');
const resultDiv = document.getElementById('result');
const errorDiv = document.getElementById('error');
const brandSelect = document.getElementById('brand');
const modelSelect = document.getElementById('model');

async function init() {
    await loadBrands();
    await loadModels();
    attachEventListeners();
}

async function loadBrands() {
    try {
        const response = await fetch(API_BRANDS_URL);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        populateSelect(brandSelect, data.brands);
    } catch (error) {
        console.error('Error loading brands:', error);
        showError('Could not load brands. Please refresh the page.');
    }
}

async function loadModels() {
    try {
        const response = await fetch(API_MODELS_URL);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        populateSelect(modelSelect, data.models);
    } catch (error) {
        console.error('Error loading models:', error);
        showError('Could not load models. Please refresh the page.');
    }
}

function populateSelect(selectElement, options) {
    selectElement.innerHTML = '<option value="">Select an option</option>';
    options.forEach(option => {
        const opt = document.createElement('option');
        opt.value = option;
        opt.textContent = option;
        selectElement.appendChild(opt);
    });
}

function showError(message) {
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    setTimeout(() => {
        errorDiv.style.display = 'none';
    }, 5000);
}

function showResult(price, formattedPrice) {
    resultDiv.innerHTML = `
        <h2>Predicted Price</h2>
        <div class="price">${formattedPrice}</div>
        <p class="note">This is an estimated price based on market data and similar listings</p>
        <p class="note" style="font-size: 0.8em; margin-top: 10px;"> Exact price: Rs.${price.toFixed(2)}</p>
    `;
    resultDiv.style.display = 'block';
    
    resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function getFormData() {
    return {
        km_driven: parseFloat(document.getElementById('km_driven').value),
        mileage: parseFloat(document.getElementById('mileage').value),
        engine: parseFloat(document.getElementById('engine').value),
        max_power: parseFloat(document.getElementById('max_power').value),
        seats: parseFloat(document.getElementById('seats').value),
        car_age: parseInt(document.getElementById('car_age').value),
        fuel: document.getElementById('fuel').value,
        seller_type: document.getElementById('seller_type').value,
        transmission: document.getElementById('transmission').value,
        owner: document.getElementById('owner').value,
        brand: document.getElementById('brand').value,
        model: document.getElementById('model').value
    };
}

function validateForm(data) {
    if (!data.km_driven || data.km_driven <= 0) {
        showError('Please enter valid kilometers driven');
        return false;
    }
    
    if (!data.mileage || data.mileage <= 0) {
        showError('Please enter valid mileage');
        return false;
    }
    
    if (!data.engine || data.engine <= 0) {
        showError('Please enter valid engine displacement');
        return false;
    }
    
    if (!data.max_power || data.max_power <= 0) {
        showError('Please enter valid max power');
        return false;
    }
    
    if (!data.car_age || data.car_age < 0) {
        showError('Please enter valid car age');
        return false;
    }
    
    if (!data.brand) {
        showError('Please select a brand');
        return false;
    }
    
    if (!data.model) {
        showError('Please select a model');
        return false;
    }
    
    return true;
}

function setButtonLoading(isLoading) {
    if (isLoading) {
        predictBtn.disabled = true;
        predictBtn.textContent = 'Predicting...';
    } else {
        predictBtn.disabled = false;
        predictBtn.textContent = 'Predict Price';
    }
}

async function handleSubmit(event) {
    event.preventDefault();
    
    resultDiv.style.display = 'none';
    errorDiv.style.display = 'none';
    
    const formData = getFormData();
    
    if (!validateForm(formData)) {
        return;
    }
    
    setButtonLoading(true);
    
    try {
        const response = await fetch(API_PREDICT_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showResult(data.predicted_price, data.formatted_price);
        } else {
            showError(data.message || 'Prediction failed');
        }
        
    } catch (error) {
        console.error('Prediction error:', error);
        showError(`Failed to get prediction: ${error.message}. Make sure the server is running.`);
    } finally {
        setButtonLoading(false);
    }
}

function fillExample() {
    document.getElementById('km_driven').value = '50000';
    document.getElementById('mileage').value = '18.5';
    document.getElementById('engine').value = '1498';
    document.getElementById('max_power').value = '88';
    document.getElementById('seats').value = '5';
    document.getElementById('car_age').value = '5';
    document.getElementById('fuel').value = 'Diesel';
    document.getElementById('seller_type').value = 'Individual';
    document.getElementById('transmission').value = 'Manual';
    document.getElementById('owner').value = 'Second Owner';
    
    setTimeout(() => {
        if (brandSelect.options.length > 1) {
            brandSelect.value = 'Hyundai';
        }
        if (modelSelect.options.length > 1) {
            modelSelect.value = 'i20';
        }
    }, 500);
}

function attachEventListeners() {
    form.addEventListener('submit', handleSubmit);
    
    const numberInputs = ['km_driven', 'mileage', 'engine', 'max_power', 'car_age'];
    numberInputs.forEach(inputId => {
        const input = document.getElementById(inputId);
        input.addEventListener('input', function() {
            if (this.value < 0) this.value = 0;
        });
    });
    
    document.addEventListener('keydown', function(e) {
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            form.dispatchEvent(new Event('submit'));
        }
    });
}

function addExampleButton() {
    const buttonContainer = document.createElement('div');
    buttonContainer.style.marginTop = '10px';
    buttonContainer.style.textAlign = 'center';
    
    const exampleBtn = document.createElement('button');
    exampleBtn.type = 'button';
    exampleBtn.textContent = 'Load Example Car';
    exampleBtn.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
    exampleBtn.style.opacity = '0.8';
    exampleBtn.style.marginTop = '0';
    
    exampleBtn.onclick = fillExample;
    buttonContainer.appendChild(exampleBtn);
    
    form.parentNode.insertBefore(buttonContainer, form.nextSibling);
}

document.addEventListener('DOMContentLoaded', () => {
    init();
    addExampleButton();
});