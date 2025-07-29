import json

import streamlit.components.v1 as components


def copy_to_clipboard(text: str):
    """
    Copies the given text to the clipboard using the new, secure method.
    Only work on HTTPS and newer browsers.
    """
    # JSON-encode text to safely embed into JavaScript string literal
    js_text = json.dumps(text)

    download_html = f"""
<html>
    <body style="margin:0;padding:0;">
        <!-- Invisible button to trigger clipboard copy -->
        <button
            id="btnCopy"
            style="
                width:0;
                height:0;
                padding:0;
                margin:0;
                border:none;
                background:transparent;
            ">
        </button>

        <script>
            // The text to be copied
            const textToCopy = {js_text};

            // Add event listener on the invisible button
            document.getElementById('btnCopy').addEventListener('click', () => {{
                // Use the modern Clipboard API to copy text
                parent.navigator.clipboard.writeText(textToCopy)
                    .then(() => console.log('[Clipboard] Copy successful:', textToCopy))
                    .catch(err => console.error('[Clipboard] Copy failed:', err));
            }});

            // Programmatically click the button to trigger the copy
            document.getElementById('btnCopy').click();
        </script>
    </body>
</html>
"""

    # Render the HTML with zero height so it doesn't affect layout
    components.html(download_html, height=0)


def copy_to_clipboard_unsecured(text: str):
    """
    Copies the given text to the clipboard using the legacy method.
    Work on both HTTP and HTTPS, and even in older browsers.
    """
    # JSON-encode text to safely embed into JavaScript string literal
    js_text = json.dumps(text)

    download_html = f"""
<html>
    <body style="margin:0;padding:0;">
        <script>
            /**
             * Copies text to clipboard by creating and selecting a hidden textarea.
             * Uses document.execCommand('copy'), which is deprecated but widely supported.
             */
            function unsecuredCopyToClipboard(text) {{
                // Create a hidden textarea element
                const textArea = document.createElement("textarea");
                textArea.value = text;

                // Append to the parent document body
                parent.document.body.appendChild(textArea);

                // Focus and select the textarea content
                textArea.focus();
                textArea.select();

                try {{
                    // Execute the copy command
                    const successful = parent.document.execCommand('copy');
                    if (successful) {{
                        console.log('[Clipboard] execCommand copy succeeded:', text);
                    }} else {{
                        console.warn('[Clipboard] execCommand copy returned false');
                    }}
                }} catch (err) {{
                    console.error('[Clipboard] execCommand copy failed:', err);
                }}

                // Remove the textarea element
                parent.document.body.removeChild(textArea);
            }}

            // Call the function immediately with the given text
            unsecuredCopyToClipboard({js_text});
        </script>
    </body>
</html>
"""

    # Render the HTML with zero height so it doesn't affect layout
    components.html(download_html, height=0)