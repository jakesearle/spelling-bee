# README

* How many puzzles are possible?
  * 52,729 valid puzzles
  * 97,841 invalid puzzles
* Which puzzles are funnest? Least fun? What metrics could you use to measure fun?
  - [X] Number of words?
  - [X] Common-ness of words?
  - [X] Length of words?
  - [ ] Sentiment analysis of Reddit posts?
* Are there any puzzles that have the letters for "ING", "LY" etc. but never use them together in a word?
  * For the ngrams "ING" and "ED", no.
  * For "LY", this has happened twice:
    * April 03, 2024 | (P) E I K L U Y
    * December 01, 2020 | (T) B I L M O Y
* What have been longest non-pangram words?
  * 'INCONVENIENCE' and 'CATALYTICALLY', which have appeared in puzzles on January 14, 2024, October 21, 2022, 
January 22, 2021, February 17, 2020, April 06, 2019, and September 27, 2018
* Has a pangram ever been removed from the dictionary?
  * Yes.
  * NONDORMANT
  * MANDATOR
  * CONIFORM
  * ADAPTION
* Has there ever been a repeat puzzle?
* What do unverified words look like?

## Glossary

- Verified words - Have been confirmed to be a word you could enter and score today 
- Illegal words - Have been confirmed to be a word you could *not* enter and score today
- Unverified words - Have not been proven one way or another, and are valid 2019 Collins Scrabble dictionary words
- Retconned words - Were "verified" at one point in time, that are now "illegal" today.
- Likely words - A subset of "unverified words" that *could* be in a future puzzle, according to the following rules
  - Do not contain an "S"
  - Do not contain an "E" and "R"
  - Do not contain 8 or more unique letters


## Pokédex Clarification
I've scraped the list of Pokémon names from [Bulbapedia](https://bulbapedia.bulbagarden.net/wiki/List_of_Pok%C3%A9mon_by_National_Pok%C3%A9dex_number).
* 'MUK' and 'MEW' (the only Pokémon names of length <4) are valid because why not
* "NIDORAN" without '♀' or '♂' *is* valid
* The following Pokémon were excluded:
  * Pokémon with punctuation: "FARFETCH'D", "HO-OH", etc.
  * Pokémon with numbers: "PORYGON2"
  * Pokémon with diacritics : "FLABÉBÉ"
  * Pokémon with spaces: "MR. MIME", "TAPU KOKO", "ROARING MOON", etc.

## Todo:
- Improve iteration over puzzles
- Pokedex words

>!Column L | Column C | Column R!<
