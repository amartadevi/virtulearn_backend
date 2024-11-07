import g4f

class AIQuizManager:
    def generate_quiz(self, notes_content):
        # Create prompt to generate a quiz based on the notes content
        prompt = f"""Please generate a quiz based on these notes: {notes_content}. Provide five questions and their answer with four options each. 

        Make sure to follow this format for quiz generation:
        Start with the number followed by the question.
        A) Option A
        B) Option B
        C) Option C
        D) Option D
        Correct Answer: X
        """
        
        # Call the AI model
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that generates quizzes."},
                {"role": "user", "content": prompt}
            ]
        )

        if isinstance(response, dict):
            quiz_content = response['choices'][0]['message']['content']
        else:
            quiz_content = response

        return quiz_content