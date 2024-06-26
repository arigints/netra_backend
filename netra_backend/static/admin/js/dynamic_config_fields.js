// static/admin/js/dynamic_config_fields.js
document.addEventListener('DOMContentLoaded', function() {
    function addConfigFields(componentName) {
        const addButton = document.createElement('button');
        addButton.type = 'button';
        addButton.innerText = `Add ${componentName} Config`;
        document.querySelector('.submit-row').appendChild(addButton);

        addButton.addEventListener('click', function() {
            const formRow = document.createElement('div');
            formRow.className = 'form-row';

            const keyField = document.createElement('input');
            keyField.type = 'text';
            keyField.name = `${componentName}_config_key`;
            keyField.placeholder = 'Config Key';
            keyField.className = 'vTextField';

            const valueField = document.createElement('input');
            valueField.type = 'text';
            valueField.name = `${componentName}_config_value`;
            valueField.placeholder = 'Config Value';
            valueField.className = 'vTextField';

            const removeButton = document.createElement('button');
            removeButton.type = 'button';
            removeButton.innerText = 'Remove';
            removeButton.addEventListener('click', function() {
                formRow.remove();
            });

            formRow.appendChild(keyField);
            formRow.appendChild(valueField);
            formRow.appendChild(removeButton);
            document.querySelector('form').insertBefore(formRow, document.querySelector('.submit-row'));
        });
    }

    addConfigFields('CU');
    addConfigFields('DU');
    addConfigFields('UE');
});
