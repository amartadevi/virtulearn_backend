import g4f

class AINotesManager:
    def generate_notes(self, topic):
        try:
            print(f"Generating notes for topic: {topic}")
            prompt = f"Please generate concise notes covering key concepts, stages, and processes for the following topics: {topic}. Keep the content formal and limited to a maximum of 1000 words in bullet points."
            
            # Call the AI model
            response = g4f.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant that generates notes."},
                    {"role": "user", "content": prompt}
                ]
            )

            # Print the response for debugging
            print(f"AI response: {response}")
            
            # Ensure we return a string
            if isinstance(response, dict):
                notes = response.get('choices', [{}])[0].get('message', {}).get('content', '')
            else:
                notes = str(response)

            return notes

        except Exception as e:
            print(f"Error in generate_notes: {e}")
            return f"Error generating notes: {str(e)}"
