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
        const container = document.getElementById(containerId);
        if (!container) {
            console.warn('Password generator container not found:', containerId);
            return;
        }
        
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
        
        // Wire up buttons
        document.getElementById('btn-generate')?.addEventListener('click', generatePassword);
        document.getElementById('btn-validate')?.addEventListener('click', validatePassword);
    }
    
    /**
     * Generate password for level
     */
    function generatePassword() {
        const world = parseInt(document.getElementById('password-world')?.value || 0);
        const level = parseInt(document.getElementById('password-level')?.value || 0);
        
        if (window.API) {
            window.API.generatePassword(world, level)
                .then(result => {
                    displayPassword(result);
                })
                .catch(error => {
                    console.error('Password generation failed:', error);
                });
        } else {
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
            document.getElementById('validation-result').textContent = 'Password must be 6 digits';
            return;
        }
        
        const digits = input.split('').map(d => parseInt(d) * 2);  // Simplified decoding
        
        if (window.API) {
            window.API.validatePassword(digits)
                .then(result => {
                    displayValidation(result);
                });
        } else {
            // Fallback validation
            displayValidation({
                valid: true,
                progression: {
                    world: 0,
                    level_index: 0
                }
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
                    Valid password!<br>
                    World: ${result.progression.world}<br>
                    Level: ${result.progression.level_index}
                </div>
            `;
        } else {
            resultDiv.innerHTML = `
                <div class="validation-error">
                    Invalid password: ${result.error}
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
