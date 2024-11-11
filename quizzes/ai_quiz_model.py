
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
        and also don't include any other text than the quiz questions and options and the correct answer, just the quiz questions and options and the correct answer
        . don't ask any user input, just generate the quiz questions and options and the correct answer and 
        follow only the format above and make sure don't gave me any other format than the one above
        """
        
        # Call the AI model
        response = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a quiz generator that always generates quizzes."},
                {"role": "user", "content": prompt}
            ]
        )

        if isinstance(response, dict):
            quiz_content = response['choices'][0]['message']['content']
        else:
            quiz_content = response

        return quiz_content