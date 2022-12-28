import datetime
from typing import List,Tuple

class Card:
    def __init__(self,answer,question,quality:int,easiness_factor,interval,is_new:bool,last_study):
        self.question = question
        self.answer=answer
        self.quality=quality #a quality is a number from 1 to 4
        self.easiness_factor = easiness_factor
        self.interval = interval
        self.is_new = is_new
        self.last_study = datetime.now()
        #remove the datime from the database?

    def study(self):
        '''
        Calculate the new interval based on the easiness factor, quality and interval.
        Reducing the minimum easiness factor below 1.3 would make it repeat a lot more often, unnecessarily.
        if the quality is more than 3 but the easiness factor is more than the
        the base limits we modify the easiness factor to make it stop it repeating too much or too little      
        '''

        #default variables are set if the cards are new
        if self.is_new:
            self.easiness_factor = 2.5
            self.interval = 1
            self.is_new=False
            return self.easiness_factor, self.interval
        elif self.quality <3:
            self.easiness_factor = 2.5
            self.interval = 1
            return self.easiness_factor, self.interval
        else:# If the easiness factor is outside the base limits, modify it to prevent it from repeating too much or too little 
            if self.easiness_factor < 1.3:
                self.easiness_factor = 1.3
            elif self.easiness_factor > 2.5:
                self.easines_factor =2.5
            new_easiness_factor =  new_interval = 0
            self.new_easiness_factor += self.easiness_factor + (0.1 - (5 - self.quality) * (0.08 + (5 - self.quality) * 0.02))
            new_interval = self.interval * new_easiness_factor
            self.easiness_factor = new_easiness_factor
            self.interval = new_interval
            self.last_reviewed = datetime.now()
            return self.interval,self.easiness_factor
        
    def study_due(self) -> bool:
        try:
            review_interval = timedelta(days=self.interval)#converts int to time using datetime
            return self.last_reviewed + review_interval <= datetime.now()
        except TypeError:
            # Handle TypeError if self.interval is not an integer
            print("Error: Interval must be an integer")
            return False
        except ValueError:
            # Handle ValueError if self.interval is a negative integer
            print("Error: Interval must be a positive integer")
            return False 
            

class Flashcard(Card):
    def __init__(self,question,answer,quality:int):
        super().__init__(question,answer,quality)
        self.quality = quality

#Check if this even works, the gaps thing is a bit fiddily on how gaps will be passed when created
class Fill_the_gaps(Card):
    def __init__(self,question,answer,gaps,quality:int):
        '''
        This will be another type of flashcard, a flashcard where answer is shown when reviewed, apart from some missing gaps indicated by the user
        '''
        #overrides the class inherited from, only put in items inherited
        super().__init__(question,answer,quality)

class Multi_choice(Card):
    def __init__(self,question,answer,quality,choice:List):
        super().__init__(question,answer,quality)

class Deck:
    def __init__(self,name:str,flashcards:List,subdecks:List[Deck] = None):
        self.name = name
        self.flashcards = flashcards
        if subdecks:
            self.subdecks = subdecks
        else:
            self.subdecks = []

class User:
    def __init__(self,id,decks):
        self.id = current_user.get_id() 
        self.decks = decks

def study_flashcard(flashcard):
    studied_flashcards = []
    #f as in flashcard, just to avoid errors/confusion with flashcard class
    for f in flashcards:
        result= flashcard.study()
        cards_studied.append((flashcard,result))
    return cards_studied


def study_deck(deck: Deck) -> List[Tuple[Card,int]]:
    #if flashcard filters out the flashcard in the list, to only output flashcards that are due
    card_due = [f for f in deck.flashcards if self.study(flashcard)]
    card_due.extend(review_flashcards(Flashcards_to_Review))
    for subdeck in deck.subdecks:
        reviewed_flashcards.extend(review_deck(subdecks))

    return study_flashcard(card_due)

def user_decks(user) -> List[Tuple[Card,int]]:
    flashcards_studied = []
    for deck in user.decks:
        reviewed_flashcard.extend(review_deck(Deck))
    return flashcards_studied


flashcard1 = Flashcard('Whats the capital of france?','Paris')
deck = Deck('Country capitals',flashcard1)
user=review_user(deck=deck)
review_results = review_user(user)


