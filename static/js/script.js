document.addEventListener('DOMContentLoaded', function() {
    
    // 1. SEARCH FUNCTIONALITY
    const searchInput = document.getElementById('searchBar');
    searchInput.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        const items = document.querySelectorAll('.symptom-item');

        items.forEach(function(item) {
            const label = item.querySelector('label');
            const text = label.textContent || label.innerText;
            if (text.toLowerCase().includes(filter)) {
                item.style.display = "";
            } else {
                item.style.display = "none";
            }
        });
    });

    // 2. SELECTED SYMPTOMS PREVIEW
    const checkboxes = document.querySelectorAll('input[name="symptoms"]');
    const selectionContainer = document.getElementById('selection-container');
    const selectionBox = document.getElementById('selected-symptoms-box');

    function updatePreview() {
        // Clear current tags
        selectionContainer.innerHTML = '';
        
        // Find all checked boxes
        const checkedBoxes = document.querySelectorAll('input[name="symptoms"]:checked');
        
        if (checkedBoxes.length > 0) {
            selectionBox.style.display = "block"; // Show the box
            
            checkedBoxes.forEach(function(box) {
                // Create the tag
                const tag = document.createElement('span');
                tag.className = 'symptom-tag';
                // Get the text from the label (e.g., "High Fever")
                const labelText = box.parentElement.textContent.trim();
                
                tag.innerHTML = `${labelText} <span class="remove-btn" data-val="${box.value}">&times;</span>`;
                selectionContainer.appendChild(tag);
            });

            // Add click listeners to the new "X" buttons
            document.querySelectorAll('.remove-btn').forEach(function(btn) {
                btn.addEventListener('click', function() {
                    const val = this.getAttribute('data-val');
                    // Uncheck the original box
                    const originalBox = document.querySelector(`input[value="${val}"]`);
                    if (originalBox) originalBox.checked = false;
                    // Refresh the preview
                    updatePreview();
                });
            });

        } else {
            selectionBox.style.display = "none"; // Hide if empty
        }
    }

    // Attach listener to every checkbox
    checkboxes.forEach(function(box) {
        box.addEventListener('change', updatePreview);
    });

    // 3. FORM VALIDATION
    const form = document.querySelector('form');
    form.addEventListener('submit', function(event) {
        const checked = document.querySelectorAll('input[name="symptoms"]:checked');
        if (checked.length === 0) {
            event.preventDefault();
            alert("Please select at least one symptom before predicting.");
        }
    });
});