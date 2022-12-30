from typing import List,Tuple
from datetime import datetime,timedelta

class Deck:

    def __init__(self,name:str,flashcards:List[card],subdecks = None):
        self.name = name
        self.flashcards = flashcards#make it an object when you submit, so there can be different types of flashcards
        self.card = Card()
        if subdecks:
            self.subdecks = subdecks
        else:
            self.subdecks = []
    
    def add_card(self,card:Card):#maybe take in an input e.g. deck id?
        self.flashcards.append(card)

#card= Card(answer='',question='')
#deck.add_card(card)
    def get_decks(self):
        '''
        Returns a list of all decks and subdecks within a deck
        '''
        all_decks = [self] # starts with the main deck
        for subdeck in self.subdecks:
            #Recursion
            all_decks.extend(subdeck.get_decks())
        return all_decks

    def is_card_due(self) -> bool:
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

    def study_flashcard(self):
        studied = []
        #f as in flashcard, just to avoid errors/confusion with flashcard class
        for flashcard in flashcards:
            result = flashcard.study()
            studied.append((flashcard,result))
        return studied

    def study_deck(self) -> List[Tuple[Card,int]]: #(card, rating)
        #if flashcard filters out the flashcard in the list, to only output flashcards that are due
        card_due = [card for card in self.flashcards if card.is_study_due()]#card, not the attribute self.card
        card_due.extend(self.study_flashcard(Flashcards_to_Review))

        for subdeck in self.subdecks:
            card_due.extend(subdeck.study_deck())

        return study_flashcard(card_due)

class User:
    def __init__(self,id,decks):
        self.id = current_user.get_id() 
        self.decks = decks

class Card:
    def __init__(self,answer,question,is_new:bool,quality:int = None,easiness_factor = None,interval = None):
        self.question = question
        self.answer=answer
        self.is_new = is_new
        self.quality=quality #a quality is a number from 1 to 4
        self.easiness_factor = easiness_factor
        self.interval = interval
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


            

# class Flashcard(Card):
#     def __init__(self,question,answer,quality:int):
#         super().__init__(question,answer,quality)
        

#Check if this even works, the gaps thing is a bit fiddily on how gaps will be passed when created
#Fill in the gaps and the choice will need to be rendered differnetly so fix this later,
class Fill_the_gaps(Card):
    def __init__(self,answer,question,quality:int,easiness_factor,interval,is_new:bool,last_study,gaps):
        '''
        This will be another type of flashcard, a flashcard where answer is shown when reviewed, apart from some missing gaps indicated by the user
        '''
        #overrides the class inherited from, only put in items inherited
        super().__init__(answer,question,quality,easiness_factor,interval,is_neww,last_study)
        self.gaps = gaps

class Multi_choice(Card):
    def __init__(self,answer,question,quality:int,easiness_factor,interval,is_new:bool,last_study,choice:List):
        super().__init__(self,answer,question,quality,easiness_factor,interval,is_new,last_study)
        self.choice = choice

#
def finds_cards(user) -> List[Tuple[Card,int]]:
    flashcards_studied = []
    for deck in user.decks:
        reviewed_flashcard.extend(deck.study_deck(Deck))
    return flashcards_studied


# flashcard1 = Card('Whats the capital of france?','Paris',is_new = True)
# deck = Deck('Country capitals',flashcard1)
# user=user_deck(deck=deck)
# review_results = review_user(user)
# all_decks = top_level_deck.get_all_decks()

deck1 = Deck("Deck 1", [])
deck2 = Deck("Deck 2", [])
subdeck1 = Deck("Subdeck 1", [], [deck2])
subdeck2 = Deck("Subdeck 2", [])
top_level_deck = Deck("Top Level Deck", [], [subdeck1, subdeck2])
all_decks = 0
all_decks = top_level_deck.get_decks()
for deck in all_decks:
    print(deck.name)



