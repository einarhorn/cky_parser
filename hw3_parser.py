#!/usr/bin/env python3
import sys
import nltk

class CKYEntry:
    def __init__(self, nltk_node, parents = []):
        self.nltk_node = nltk_node
        self.parents = parents


class CKYParser:
    def __init__(self, grammar):
        self.grammar = grammar
    
    def parse_sentence(self, sentence):
        tokenized_sentence = nltk.word_tokenize(sentence)
        return self.parse_tokenized_sentence(tokenized_sentence)

    def parse_tokenized_sentence(self, tokenized_sentence):
        # Build our square CKY table
        # Table will be (n + 1) x (n + 1), where n is len(tokenized_sentence)
        width = height = len(tokenized_sentence) + 1

        # Each cell [i][j] contains a set of CKYEntry items
        table = [[set() for x in range(width)] for y in range(height)] 
    
        # We fill from left to right, bottom to top, for the top right triangle
        for j in range(1, width):
            # First fill in a terminal cell
            current_word = tokenized_sentence[j - 1]
            table[j - 1, j] = calculate_diagonal_cell(current_word)

            # Iterate over cells in upward direction from bottom-most cell
            for i in range(j - 2, 0, -1):
                for k in range(i + 1, j - 1):
                    updated_entry = calculate_intermediate_cell(i, j, k)
                    table[i, j] = table[i, j].union(updated_entry)

    # Return set of CKYEntrys, which correspond to nonterminals with current_word as a rhs terminal
    def calculate_diagonal_cell(current_word):
        # Search productions to find all lhs nonterminals that have current_word as a rhs terminal
        releveant_productions = grammar.productions(rhs=current_word)

        # Get LHS of each of the productions
        productions_lhs = {production.lhs() for production in releveant_productions}

        # Convert to a set of CKYEntry items
        return {CKYEntry(nonterminal) for nonterminal in nonterminals}

    # Calculate intermediate cells, based on two previously calculated cells
    # {A | A → BC ∈ grammar,
    #   B ∈ table[ i, k ],
    #   C ∈ table[ k, j ]
    # }
    def calculate_intermediate_cell(i, j, k):
        # Set containing the CKYEntrys we want to return
        cell_contents = set()

        # Get contents of the two cells we will be using
        first_set = table[i,k]
        second_set = table[k,j]

        # Calculate every combination of first and second cell
        for first_set_item in first_set:
            for second_set_item in second_set:
                # Check whether there is a production A -> B C, where B is first_set_item
                # and B is second_set_item
                releveant_productions = get_productions_with_rhs(first_set_item, second_set_item)

                # Get LHS of each of the productions
                productions_lhs = {production.lhs() for production in releveant_productions}

                # Convert each LHS entry to a CKYEntry item
                node_parents = [first_set_item, second_set_item]
                cky_entries = {CKYEntry(productions_lhs, node_parents) for production_lhs in productions_lhs}

                # Union with our set of valid CKYEntry items created so far
                cell_contents = cell_contents.union(cky_entries)
        
        return cell_contents
                


def main(grammar_filename, sentence_filename, output_filename):
    # Load CNF grammar
    grammar = nltk.data.load(grammar_filename, 'cfg')

    # Generate parser based on grammar
    parser = CKYParser(grammar)

    # Iterate over sentences in sentence_filename and produce parses
    sentence_file = open(sentence_filename)
    for line in sentence_file:
        # Strip any trailing whitespace from line (including newlines)
        line = line.rstrip()
        parser.parse_sentence(line)

    # Output parse data to output_filename


if __name__ == "__main__":
    # Get number of args (-1 to exclude the original file being counted as arg)
    num_args = len(sys.argv) - 1

    # Required number of args for program to run
    required_args = 3

    # Verify correct number of args passed
    if num_args >= required_args:
        grammar_filename = sys.argv[1]
        sentence_filename = sys.argv[2]
        output_filename = sys.argv[3]
    else:
        print("Invalid number of arguments. Expected:", file=sys.stderr)
        print("hw3_parser.sh <grammar_filename> <test_sentence_filename> <output_filename>", file=sys.stderr)
        sys.exit()
    main(grammar_filename, sentence_filename, output_filename)


