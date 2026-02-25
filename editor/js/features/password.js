/**
 * Password Generator for Space Funky B.O.B. Level Editor
 * 
 * 6-digit password generation/validation UI.
 * NEW FEATURE - Source-verified from INITLEVE.A:passwords
 */

(function() {
    'use strict';
    
    /**
     * Initialize password generator UI
     * @param {string} containerId - Container element ID
     */
    function initPasswordGenerator(containerId) {
        Logger.info('PasswordGenerator', 'initPasswordGenerator called with containerId: ' + containerId);
        const container = document.getElementById(containerId);
        Logger.info('PasswordGenerator', 'Container element: ' + (container ? 'found' : 'NOT FOUND'));
        if (!container) {
            Logger.warn('PasswordGenerator', 'Container not found: ' + containerId);
            return;
        }

        Logger.info('PasswordGenerator', 'Building password generator UI...');
        container.innerHTML = `
            <div class="password-generator">
                <h3>Password Generator</h3>
                <div class="password-form">
                    <label>
                        World:
                        <select id="password-world">
                            <option value="0">World 0 (Borg Factory)</option>
                            <option value="1">World 1 (Bug Planet)</option>
                            <option value="2">World 2 (Ancient Ruins)</option>
                        </select>
                    </label>
                    <label>
                        Level:
                        <input type="number" id="password-level" min="0" max="18" value="0">
                    </label>
                    <button id="btn-generate">Generate Password</button>
                </div>
                <div id="password-result" class="password-result"></div>
                <div id="password-validate" class="password-validate">
                    <h4>Validate Password</h4>
                    <input type="text" id="password-input" maxlength="6" placeholder="Enter 6-digit password">
                    <button id="btn-validate">Validate</button>
                    <div id="validation-result"></div>
                </div>
            </div>
        `;

        Logger.info('PasswordGenerator', 'Wiring up buttons...');
        // Wire up buttons
        const genBtn = document.getElementById('btn-generate');
        const valBtn = document.getElementById('btn-validate');
        Logger.info('PasswordGenerator', 'Generate button: ' + (genBtn ? 'found' : 'NOT FOUND'));
        Logger.info('PasswordGenerator', 'Validate button: ' + (valBtn ? 'found' : 'NOT FOUND'));
        
        genBtn?.addEventListener('click', () => {
            Logger.info('PasswordGenerator', 'Generate button clicked');
            generatePassword();
        });
        valBtn?.addEventListener('click', () => {
            Logger.info('PasswordGenerator', 'Validate button clicked');
            validatePassword();
        });
        
        Logger.info('PasswordGenerator', 'Password generator initialization complete');
    }

    /**
     * Generate password for level
     */
    function generatePassword() {
        Logger.info('PasswordGenerator', 'generatePassword called');
        const worldEl = document.getElementById('password-world');
        const levelEl = document.getElementById('password-level');
        Logger.info('PasswordGenerator', 'World element: ' + (worldEl ? 'found' : 'NOT FOUND'));
        Logger.info('PasswordGenerator', 'Level element: ' + (levelEl ? 'found' : 'NOT FOUND'));
        
        const world = parseInt(worldEl?.value || 0);
        const level = parseInt(levelEl?.value || 0);
        Logger.info('PasswordGenerator', 'World: ' + world + ', Level: ' + level);

        if (window.API) {
            Logger.info('PasswordGenerator', 'Calling API.generatePassword...');
            window.API.generatePassword(world, level)
                .then(result => {
                    Logger.info('PasswordGenerator', 'Password generated: ' + JSON.stringify(result));
                    displayPassword(result);
                })
                .catch(error => {
                    Logger.error('PasswordGenerator', 'Password generation failed: ' + error.message);
                });
        } else {
            Logger.warn('PasswordGenerator', 'API not available, using fallback');
            // Fallback: generate simple password
            const digits = [];
            const seed = (world * 100) + level;
            for (let i = 0; i < 6; i++) {
                digits.push((seed + i * 7) % 10);
            }
            displayPassword({
                world,
                level_index: level,
                password: {
                    digits,
                    display: digits.join('')
                }
            });
        }
    }
    
    /**
     * Display generated password
     * @param {Object} result - Password result
     */
    function displayPassword(result) {
        const resultDiv = document.getElementById('password-result');
        if (!resultDiv) return;
        
        resultDiv.innerHTML = `
            <div class="password-display">
                <div class="password-digits">${result.password.display}</div>
                <div>World: ${result.world}, Level: ${result.level_index}</div>
            </div>
        `;
    }
    
    /**
     * Validate password
     */
    function validatePassword() {
        const input = document.getElementById('password-input')?.value || '';

        if (input.length !== 6) {
            displayValidation({
                valid: false,
                error: 'Password must be 6 digits'
            });
            return;
        }

        // Validate all characters are digits
        if (!/^\d{6}$/.test(input)) {
            displayValidation({
                valid: false,
                error: 'Password must contain only digits 0-9'
            });
            return;
        }

        Logger.info('PasswordGenerator', 'Validating password: ' + input);

        if (window.API) {
            Logger.info('PasswordGenerator', 'Calling API.validatePassword...');
            window.API.validatePassword(input)
                .then(result => {
                    Logger.info('PasswordGenerator', 'Validation result: ' + JSON.stringify(result));
                    displayValidation(result);
                })
                .catch(error => {
                    Logger.error('PasswordGenerator', 'Validation failed: ' + error.message);
                    displayValidation({
                        valid: false,
                        error: error.message
                    });
                });
        } else {
            Logger.warn('PasswordGenerator', 'API not available');
            displayValidation({
                valid: false,
                error: 'API not available'
            });
        }
    }
    
    /**
     * Display validation result
     * @param {Object} result - Validation result
     */
    function displayValidation(result) {
        const resultDiv = document.getElementById('validation-result');
        if (!resultDiv) return;

        if (result.valid) {
            resultDiv.innerHTML = `
                <div class="validation-success">
                    ✓ Valid password!<br>
                    World: ${result.world}<br>
                    Level: ${result.level_index}<br>
                    <small>${result.message || ''}</small>
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="validation-error">
                    ✗ ${result.error || 'Invalid password'}
                </div>
            `;
        }
    }
    
    // Export to window
    window.PasswordGenerator = {
        initPasswordGenerator,
        generatePassword,
        validatePassword,
        displayPassword,
        displayValidation
    };
    
})();
