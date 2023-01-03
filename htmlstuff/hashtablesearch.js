// Define a function to create a hash table
function createHashTable() {
  // Initialize the hash table with an array of null values
  const table = new Array(10).fill(null);

  // Define a function to calculate the hash of a key
  function hash(key) {
    let sum = 0;
    for (let i = 0; i < key.length; i++) {
      sum += key.charCodeAt(i);
    }
    return sum % table.length;
  }

  // Define a function to add a key-value pair to the hash table
  function add(key, value) {
    // Calculate the hash of the key
    const index = hash(key);

    // Check if the hash table has any values at the calculated index
    if (table[index] === null) {
      // If the index is empty, add the key-value pair to the hash table
      table[index] = { key, value };
    } else {
      // If the index is not empty, check if the key already exists in the hash table
      let current = table[index];
      while (current.key !== key) {
        if (current.next === null) {
          // If the key does not exist, add it to the end of the linked list at the index
          current.next = { key, value, next: null };
          return;
        }
        current = current.next;
      }
      // If the key already exists, update the value
      current.value = value;
    }
  }

  // Define a function to get the value of a key from the hash table
  function get(key) {
    // Calculate the hash of the key
    const index = hash(key);

    // Check if the hash table has any values at the calculated index
    if (table[index] === null) {
      // If the index is empty, return null
      return null;
    } else {
      // If the index is not empty, search for the key in the linked list at the index
      let current = table[index];
      while (current.key !== key) {
        if (current.next === null) {
          // If the key is not found, return null
          return null;
        }
        current = current.next;
      }
      // If the key is found, return the value
      return current.value;
    }
  }

  // Return the hash table object with the add and get functions
  return { add, get };
}

// Create a hash table to store the cards
const cardTable = createHashTable();

// Add the cards to the hash table
const cards = document.querySelectorAll(".card");
cards.forEach(function (card) {
  // Get the card title and card text
  const cardTitle = card.querySelector(".card-title").textContent;
  const cardText = card.querySelector(".card-text").textContent;

  // Add the card title and card text to the hash table
  cardTable.add(cardTitle, card);
  cardTable.add(cardText, card);
});

// Get the search input and search button elements
const searchInput = document.getElementById("search-input");
const searchButton = document.querySelector('button[type="submit"]');

// Add an event listener to the search button
searchButton.addEventListener("click", function (event) {
  // Prevent the form from submitting
  event.preventDefault();

  // Get the search input value
  const searchTerm = searchInput.value.toLowerCase();

  // Loop through all the cards
  cards.forEach(function (card) {
    // Check if the search term is present in the card title or card text
    if (cardTable.get(searchTerm) !== null) {
      // If the search term is present, show the card
      card.style.display = "block";
    } else {
      // If the search term is not present, hide the card
      card.style.display = "none";
    }
  });
});
