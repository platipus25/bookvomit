# Word Vomit

## Motivation

The project's goal is to accurately simulate and present the mass flow rate of a stream of word vomit. Imagine a small library of books collectively vomiting their pages into a pulpy stream of words.

## Simulation

Words per minute => pages per second => mass per second

Dimensions of the book will be fetched from the library of congress
The book will be downloaded from Project Gutenberg

The book will be rendered at the correct dimensions (preferably a canonical pdf version) to determine pagination

Word by word, each book will be read out into the vomit stream
and as they reach a page boundary, the flow rate counters will be updated

The weight of the paper will be assumed uniformly across all books until that data is readily available
The weight of the ink will be taken as negligable

## Paramters

- words per minute
- paper weight
- font size

## Visualization

Curses maybe?
- overall vomit mass flow rate
- vomit flow rate for each book
- page counter for each book
- vomit word stream visualization


