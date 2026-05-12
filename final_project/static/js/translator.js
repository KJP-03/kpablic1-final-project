$(document).ready(function() {
    
    // Update character and codon count on input
    $('#sequence-input').on('input', function() {
        var sequence = $(this).val().replace(/\s/g, '');
        var charCount = sequence.length;
        var codonCount = Math.floor(charCount / 3);
        var remainder = charCount % 3;
        
        $('#char-count').text(charCount);
        
        // Show codon count with remainder info
        if (remainder > 0 && charCount > 0) {
            $('#codon-count').text(codonCount + ' (+ ' + remainder + ' extra)');
        } else {
            $('#codon-count').text(codonCount);
        }
        
        hideError();
        hideWarning();
    });
    
    // Translate button click handler
    $('#translate-btn').on('click', function() {
        var sequence = $('#sequence-input').val().trim();
        
        if (!sequence) {
            showError('Please enter a DNA or RNA sequence.');
            return;
        }
        
        var cleanSequence = sequence.replace(/\s/g, '').toUpperCase();
        
        if (cleanSequence.length === 0) {
            showError('Please enter a valid sequence.');
            return;
        }
        
        if (cleanSequence.length > 300) {
            showError('Sequence exceeds maximum length of 300 characters.');
            return;
        }
        
        var validDNA = /^[ATCG]+$/;
        var validRNA = /^[AUCG]+$/;
        
        if (!validDNA.test(cleanSequence) && !validRNA.test(cleanSequence)) {
            showError('Invalid characters detected. Use only A, T, C, G (DNA) or A, U, C, G (RNA).');
            return;
        }
        
        if (cleanSequence.indexOf('T') !== -1 && cleanSequence.indexOf('U') !== -1) {
            showError('Sequence contains both T and U. Please use only DNA (ATCG) or RNA (AUCG).');
            return;
        }
        
        var $btn = $(this);
        $btn.prop('disabled', true).text('Translating...');
        
        $.ajax({
            url: 'index.cgi',
            type: 'POST',
            data: {
                action: 'translate',
                sequence: cleanSequence
            },
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    displayResult(response);
                    updateHistory(response.history);
                    hideError();
                    
                    // Show warning if there is one
                    if (response.warning) {
                        showWarning(response.warning);
                    } else {
                        hideWarning();
                    }
                } else {
                    showError(response.error);
                }
            },
            error: function(xhr, status, error) {
                showError('An error occurred while processing your request. Please try again.');
                console.error('AJAX Error:', status, error);
            },
            complete: function() {
                $btn.prop('disabled', false).text('Translate');
            }
        });
    });
    
    // Clear input button
    $('#clear-input-btn').on('click', function() {
        $('#sequence-input').val('');
        $('#char-count').text('0');
        $('#codon-count').text('0');
        $('#output-box').html('<span class="placeholder-text">Your protein sequence will appear here...</span>');
        $('#output-info').addClass('hidden');
        hideError();
        hideWarning();
    });
    
    // Clear history button
    $('#clear-history-btn').on('click', function() {
        if (!confirm('Are you sure you want to clear all translation history?')) {
            return;
        }
        
        var $btn = $(this);
        $btn.prop('disabled', true);
        
        $.ajax({
            url: 'index.cgi',
            type: 'POST',
            data: {
                action: 'clear_history'
            },
            dataType: 'json',
            success: function(response) {
                if (response.success) {
                    $('#history-list').html('<p class="no-history">No translation history yet.</p>');
                } else {
                    showError(response.message || 'Failed to clear history.');
                }
            },
            error: function() {
                showError('Failed to clear history. Please try again.');
            },
            complete: function() {
                $btn.prop('disabled', false);
            }
        });
    });
    
    // Click on history item to load it
    $(document).on('click', '.history-item', function() {
        var $item = $(this);
        var inputSeq = $item.find('.history-input .history-seq').text();
        var outputSeq = $item.find('.history-output .history-seq').text();
        var seqType = $item.find('.history-label').first().text().replace(':', '');
        
        $('#sequence-input').val(inputSeq).trigger('input');
        
        $('#output-box').html('<span class="protein-result">' + outputSeq + '</span>');
        $('#result-type').text(seqType);
        $('#result-length').text(inputSeq.length);
        $('#result-protein-length').text(outputSeq.length);
        $('#output-info').removeClass('hidden');
        
        hideWarning();
        
        $('html, body').animate({ scrollTop: 0 }, 300);
    });
    
    function displayResult(response) {
        $('#output-box').html('<span class="protein-result">' + response.protein + '</span>');
        $('#result-type').text(response.seq_type);
        $('#result-length').text(response.seq_length);
        $('#result-protein-length').text(response.protein.length);
        $('#output-info').removeClass('hidden');
    }
    
    function updateHistory(history) {
        if (!history || history.length === 0) {
            $('#history-list').html('<p class="no-history">No translation history yet.</p>');
            return;
        }
        
        var html = '';
        for (var i = 0; i < history.length; i++) {
            var entry = history[i];
            html += '<div class="history-item" data-id="' + entry.id + '">';
            html += '<div class="history-input">';
            html += '<span class="history-label">' + entry.seq_type + ':</span>';
            html += '<span class="history-seq">' + entry.input_seq + '</span>';
            html += '</div>';
            html += '<div class="history-output">';
            html += '<span class="history-label">Protein:</span>';
            html += '<span class="history-seq">' + entry.output_protein + '</span>';
            html += '</div>';
            html += '</div>';
        }
        
        $('#history-list').html(html);
    }
    
    function showError(message) {
        $('#error-display').text(message).removeClass('hidden');
    }
    
    function hideError() {
        $('#error-display').addClass('hidden');
    }
    
    function showWarning(message) {
        $('#warning-display').text(message).removeClass('hidden');
    }
    
    function hideWarning() {
        $('#warning-display').addClass('hidden');
    }
    
    $('#sequence-input').on('keydown', function(e) {
        if (e.ctrlKey && e.keyCode === 13) {
            $('#translate-btn').click();
        }
    });
    
});