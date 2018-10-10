#!/usr/bin/env python3
import sys
import nltk

# This class corresponds to a node in the parse tree
#
# nltk_node refers to a nltk nonterminal, taken from the grammar
# children refers to either - 
# 1.) a pair of CKYEntries that result from this node
#     e.g. A -> BC, A is the nltk_node, and [B, C] are the children
# 2.) a single terminal word (string)
class CKYEntry:
    def __init__(self, nltk_node, children = []):
        self.nltk_node = nltk_node
        self.children = children


# This class handles the CKY parsing algorithm
class CKYParser:
    def __init__(self, grammar):
        self.grammar = grammar

    # Parse a raw sentence, and return a list of valid parses
    def parse_sentence(self, sentence):
        tokenized_sentence = nltk.word_tokenize(sentence)
        return self.parse_tokenized_sentence(tokenized_sentence)

    # Parse a tokenized sentence, and return a list of valid parses
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
            table[j - 1][j] = self.__calculate_diagonal_cell(table, current_word)
            # Iterate over cells in upward direction from bottom-most cell
            for i in range(j - 1, -1, -1):
                for k in range(i + 1, j):
                    updated_entry = self.__calculate_intermediate_cell(table, i, j, k)
                    table[i][j] = table[i][j].union(updated_entry)

        # Helpful for visualizing table!
        # self.__visualize_table(table)
    
        # Return all top-level CKYEntry nodes
        top_level_entries = table[0][width-1]
        valid_top_level_entries = {entry for entry in top_level_entries if entry.nltk_node.symbol() == 'S'}
        return valid_top_level_entries

    # Pretty print the provided 2d list
    def __visualize_table(self, table):
        for row in table:
            row_contents = []
            for col in row:
                row_contents.append([cky_entry.nltk_node for cky_entry in list(col)])
            print(row_contents)

    # Return set of CKYEntrys, which correspond to nonterminals with current_word as a rhs terminal
    def __calculate_diagonal_cell(self, table, current_word):
        # Search productions to find all lhs nonterminals that have current_word as a rhs terminal
        releveant_productions = self.grammar.productions(rhs=current_word)

        # Get LHS of each of the productions
        productions_lhs = {production.lhs() for production in releveant_productions}

        # Convert to a set of CKYEntry items
        return {CKYEntry(nonterminal, children=[current_word]) for nonterminal in productions_lhs}

    # Calculate intermediate cells, based on two previously calculated cells
    # {A | A → BC ∈ grammar,
    #   B ∈ table[ i, k ],
    #   C ∈ table[ k, j ]
    # }
    def __calculate_intermediate_cell(self, table, i, j, k):
        # Set containing the CKYEntrys we want to return
        cell_contents = set()

        # Get contents of the two cells we will be using
        first_set = table[i][k]
        second_set = table[k][j]

        # Calculate every combination of first and second cell
        for first_set_item in first_set:
            for second_set_item in second_set:
                # Check whether there is a production A -> B C, where B is first_set_item
                # and B is second_set_item
                releveant_productions = self.__get_productions_with_rhs(first_set_item.nltk_node, second_set_item.nltk_node)

                # Get LHS of each of the productions
                productions_lhs = {production.lhs() for production in releveant_productions}

                # Convert each LHS entry to a CKYEntry item
                node_children = [first_set_item, second_set_item]
                cky_entries = {CKYEntry(production_lhs, children=node_children) for production_lhs in productions_lhs}

                # Union with our set of valid CKYEntry items created so far
                cell_contents = cell_contents.union(cky_entries)
        
        return cell_contents
    
    # Get all productions in the grammar that have both of the given RHS items
    # This method is used, since NLTK does not support searching for multiple RHS items
    def __get_productions_with_rhs(self, first_rhs, second_rhs):
        # Get all productions that contain the first_rhs nonterminal on its RHS
        productions_with_first_rhs = self.grammar.productions(rhs = first_rhs)

        # Get all productions that also contain second_rhs
        return [production for production in productions_with_first_rhs if second_rhs in production.rhs()]
                


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
        print(parser.parse_sentence(line))

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


