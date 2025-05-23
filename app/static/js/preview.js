(() => {
  'use strict';

  const Config = {
    debounceDelay: 500,
    modalTimeout: 2000,
    predictionUrl: '/home/predict',
    submitUrl: '/home/submit',
  };

  const Elements = {
    form: null,
    preview: null,
    submitBtn: null,
    modalEl: null,
    bootstrapModal: null,
  };

  let timeoutId = null;
  let isSubmitted = false;
  let submittedValues = null;

  /**
   * Initialize the module: cache elements and bind events.
   */
  function init() {
    Elements.form = document.querySelector('form');
    Elements.preview = document.getElementById('preview');
    Elements.submitBtn = Elements.form.querySelector('button[type="submit"]');
    Elements.modalEl = document.getElementById('success-modal');
    Elements.bootstrapModal = new bootstrap.Modal(Elements.modalEl);

    if (!Elements.form || !Elements.preview || !Elements.submitBtn || !Elements.modalEl) {
      console.error('Required DOM elements not found');
      return;
    }

    Elements.form.addEventListener('input', debouncedUpdate);
    Elements.form.addEventListener('change', debouncedUpdate);
    Elements.form.addEventListener('submit', handleSubmit);

    updatePreview(); // initial preview update
  }

  /**
   * Check if all required fields in the form are filled.
   * @returns {boolean}
   */
  function isFormComplete() {
    const requiredFields = Elements.form.querySelectorAll('[required]');
    return Array.from(requiredFields).every(field => {
      if (field.type === 'select-one') {
        return field.value !== '';
      }
      return field.value.trim() !== '';
    });
  }

  /**
   * Extract current form values as a key-value object.
   * @returns {Object}
   */
  function getFormValues() {
    const values = {};
    new FormData(Elements.form).forEach((value, key) => {
      values[key] = value;
    });
    return values;
  }

  /**
   * Shallow compare two objects (only direct key-value pairs).
   * @param {Object} obj1
   * @param {Object} obj2
   * @returns {boolean}
   */
  function isSameData(obj1, obj2) {
    if (!obj1 || !obj2) return false;
    const keys1 = Object.keys(obj1);
    const keys2 = Object.keys(obj2);
    if (keys1.length !== keys2.length) return false;
    return keys1.every(key => obj1[key] === obj2[key]);
  }

  /**
   * Show loading indicator in the preview area.
   */
  function showLoading() {
    Elements.preview.innerHTML = `<div role="status" aria-live="polite" class="text-center mt-4">Loading prediction...</div>`;
    Elements.preview.style.opacity = 0.5;
  }

  /**
   * Fetch prediction from server and update the preview.
   */
  async function updatePreview() {
    if (!isFormComplete()) {
      Elements.preview.innerHTML = '';
      Elements.preview.style.opacity = 0.5;
      return;
    }

    showLoading();

    try {
      const formData = new FormData(Elements.form);
      const response = await fetch(Config.predictionUrl, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        Elements.preview.innerHTML = `
          <div class="alert alert-success mt-4 text-center" role="alert">
            Predicted Optimal Price: <strong>$${data.predicted_price}</strong>
          </div>
        `;

        if (isSubmitted) {
          const currentValues = getFormValues();
          Elements.preview.style.opacity = isSameData(currentValues, submittedValues) ? 1 : 0.5;
        } else {
          Elements.preview.style.opacity = 0.5;
        }
      } else {
        Elements.preview.innerHTML = `
          <div class="alert alert-danger mt-4 text-center" role="alert">
            Error: ${data.error}
          </div>
        `;
        Elements.preview.style.opacity = 0.5;
      }
    } catch (error) {
      console.error('Error fetching prediction:', error);
      Elements.preview.innerHTML = `
        <div class="alert alert-danger mt-4 text-center" role="alert">
          Error fetching prediction. Please try again.
        </div>
      `;
      Elements.preview.style.opacity = 0.5;
    }
  }

  /**
   * Debounced handler to update preview with delay.
   */
  function debouncedUpdate() {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      const currentValues = getFormValues();

      if (isSubmitted) {
        if (isSameData(currentValues, submittedValues)) {
          Elements.preview.style.opacity = 1;
        } else {
          Elements.preview.style.opacity = 0.5;
          isSubmitted = false;
        }
      } else {
        if (isSameData(currentValues, submittedValues)) {
          isSubmitted = true;
          Elements.preview.style.opacity = 1;
        } else {
          Elements.preview.style.opacity = 0.5;
        }
      }
      updatePreview();
    }, Config.debounceDelay);
  }

  /**
   * Handle form submission event.
   * @param {Event} event
   */
  async function handleSubmit(event) {
    event.preventDefault();

    if (!isFormComplete()) {
      alert('Please fill out all required fields before submitting.');
      return;
    }

    Elements.submitBtn.disabled = true;

    try {
      const formData = new FormData(Elements.form);
      const response = await fetch(Config.submitUrl, {
        method: 'POST',
        headers: { 'X-Requested-With': 'XMLHttpRequest' },
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        isSubmitted = true;
        submittedValues = getFormValues();

        Elements.preview.innerHTML = `
          <div class="alert alert-success mt-4 text-center" role="alert">
            Predicted Optimal Price: <strong>$${data.predicted_price}</strong>
          </div>
        `;
        Elements.preview.style.opacity = 1;

        Elements.bootstrapModal.show();
        setTimeout(() => {
          Elements.bootstrapModal.hide();
        }, Config.modalTimeout);
      } else {
        alert(`Error: ${data.error}`);
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      alert('Error submitting form. Please try again.');
    } finally {
      Elements.submitBtn.disabled = false;
    }
  }

  // Initialize once DOM is ready
  document.addEventListener('DOMContentLoaded', init);
})();
