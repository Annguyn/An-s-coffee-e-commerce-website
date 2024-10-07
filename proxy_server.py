from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        if 'text' not in data:
            raise ValueError("Missing 'text' key in request payload")

        text_to_translate = data['text']
        # Perform translation logic here
        translated_text = perform_translation(text_to_translate)

        return jsonify({'translated_text': translated_text}), 200
    except ValueError as e:
        app.logger.error(f"Translation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Translation error: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500

def perform_translation(text):
    # Dummy translation function
    return text[::-1]

if __name__ == '__main__':
    app.run(debug=True)