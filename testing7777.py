from datetime import datetime, timedelta
from typing import List, Tuple

class BaseFlashcard:
    def __init__(self, question: str, answer: str):
        self.id = id
        self.question = question
        self.answer = answer
        self.last_reviewed = datetime.now()

    def study(self) -> bool:
        pass  # Implement review logic here

class Flashcard(BaseFlashcard):
    def __init__(self, question: str, answer: str):
        super().__init__(question, answer)

class MultipleChoiceFlashcard(BaseFlashcard):
    def __init__(self, question: str, answer: str, choices: List[str]):
        super().__init__(question, answer)
        self.choices = choices

class Deck:
    def __init__(self, name: str, flashcards: List[BaseFlashcard]):
        self.name = name
        self.flashcards = flashcards

class User:
    def __init__(self, username: str, password: str, decks: List[Deck]):
        self.username = username
        self.password = password
        self.decks = decks

class FlashcardManager:
    def __init__(self, user: User):
        self.user = user


class Flashcard(IFlashcard):
    __tablename__ = 'flashcards'

class MultipleChoiceFlashcard(IFlashcard):
    __tablename__ = 'multiple_choice_flashcards'
    choices = db.Column(db.String, nullable=False)


    def review_flashcards(self, flashcards: List[BaseFlashcard]) -> List[Tuple[BaseFlashcard, bool]]:
        reviewed_flashcards = []
        for flashcard in flashcards:
            result = flashcard.review()
            reviewed_flashcards.append((flashcard, result))
        return reviewed_flashcards

    def review_due(self, flashcard: BaseFlashcard) -> bool:
        review_interval = timedelta(days=1)  # Review flashcards every day
        return flashcard.last_reviewed + review_interval <= datetime.now()

    def review_deck(self, deck: Deck) -> List[Tuple[BaseFlashcard, bool]]:
        flashcards_to_review = [flashcard for flashcard in deck.flashcards if self.review_due(flashcard)]
        return self.review_flashcards(flashcards_to_review)

    def review_selected_deck(self, deck: Deck) -> List[Tuple[BaseFlashcard, bool]]:
        if deck in self.user.decks:
            return self.review_deck(deck)
        else:
            return []

# Example usage:

flashcard_manager = FlashcardManager(user)
review_results = flashcard_manager.review_selected_deck(deck)
