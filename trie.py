class Node:
    '''Node class for each object in the trie'''

    def __init__(self, label=None, data=None):
        self.label = label
        self.data = data
        self.children = dict()  # map of type => {character: Node}

    def addChild(self, key, data=None):
        self.children[key] = Node(key, data)


class Trie:
    '''data structure for the auto suggestion engine which consists of above Node class objects'''

    def __init__(self):
        self.head = Node()
        self.state = self.head
        self.state_str = ""

    def add_first_word(self, word):
        current_node = self.head
        word_finished = True

        for i in range(len(word)):
            if word[i] in current_node.children:
                current_node = current_node.children[word[i]]
            else:
                word_finished = False
                break

        # For ever new letter, create a new child node
        if not word_finished:
            while i < len(word):
                # print "word[i] -> ", word[i]
                current_node.addChild(word[i])

                current_node = current_node.children[word[i]]
                i += 1

        # Let's store the full word at the end node so we don't need to
        # travel back up the tree to reconstruct the word
        current_node.data = word

    def add(self, word):  # in the parameter it's actually sentence not word

        # initial conditions
        current_node = self.head  # starting from root node
        word_finished = True

        # first check if # of words in the word > 1 => if yes => first take care of 1st word and then rest
        if len(word.split()) > 0:
            first_word = word.split()[0]
            self.add_first_word(
                first_word)  # for first word, since we want the first word available in the "data" field as well in node data

        # for each character go till we can find the char in the trie
        for i in range(len(word)):
            if word[i] in current_node.children:
                current_node = current_node.children[word[i]]
            else:
                word_finished = False
                break

        # For ever new letter, create a new child node
        if not word_finished:
            while i < len(word):
                current_node.addChild(word[i])  # new path in trie with new children to be added
                current_node = current_node.children[word[i]]
                i += 1

        # store the full word at the end node so we don't need to
        # travel back up the tree to reconstruct the word, for efficiency purposes
        current_node.data = word

    def start_with_state(self, prefix):  # aka get_suggestion function which was asked
        """ Returns a list of all words in tree that start with prefix from the current state of the trie"""
        words = list()

        if self.state_str not in prefix:  # if state_str is smaller than prefix, go back to root node with empty string and head as state
            self.state_str = ""
            self.state = self.head
        # so basically first find out where to start from (should i start from current state or the head node)
        # and hence the state comes in handy for such purposes
        # why this helps? because most of the time, the search for prefix can be progressive and by storing the
        # from where to start, is really efficient in cases where the trie is really deep

        top_node = self.state  # start with the current state

        # Determine end-of-prefix node
        prev_str_length = len(self.state_str)
        for letter in prefix[prev_str_length:]:
            if letter in top_node.children:
                top_node = top_node.children[letter]
                self.state_str += letter  # update state string of trie
            else:
                # Prefix not in tree, go no further
                return words  # will be empty list since no letter match for children

        # first update Trie.state for next call to start_with_state function
        self.state = top_node
        # Get characters under prefix
        if top_node == self.head:
            queue = [node for key, node in top_node.children.iteritems()]
        else:
            queue = [top_node]

        # for each node in queue, check if data/ phrase exist
        while queue:
            current_node = queue.pop()

            if (current_node.data != None):

                if len(words) < 5:  # append no more than 5 phrases
                    # we do not have to go back up the trie because of data field,
                    # to improve efficiency
                    words.append(current_node.data)
                else:
                    break

            queue = [node for key, node in current_node.children.iteritems()] + queue
        return words
