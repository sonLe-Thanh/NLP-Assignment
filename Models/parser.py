from vncorenlp import VnCoreNLP

text = "Xe buýt nào đến thành phố Hồ Chí Minh?"
pathToJar = "/Users/thanhson/Documents/Course/Term202/Natural language processing/Assignment/VnCoreNLP-1.1.1.jar"

text = text.lower()
print(text)
annotator = VnCoreNLP(pathToJar, annotators="wseg", max_heap_size='-Xmx2g')
word_segmented_text = annotator.tokenize(text)
word_segmented_text = word_segmented_text[0]


class Relation:
    # A relation arc of left -> right
    def __init__(self, left, relation_name, right):
        self.left = left
        self.right = right
        self.relation_name = relation_name

    def __str__(self):
        return self.relation_name + "(" + self.left + "->" + self.right + ")"

    def __eq__(self, other):
        return self.left == other.left and self.right == other.right


class Configuration:
    def __init__(self, stack, buffer, arcs):
        self.stack = stack
        self.buffer = buffer
        self.arcs = arcs


class Transition:

    @staticmethod
    def left_arc(conf, relation):
        """
        Add dependency relation (w_j, relation, w_i), pop stack
        :param conf: the current configuration, it has 3 elements: stack, buffer, arcs
        :param relation: the relation to be added
        """
        # Precondition: Neither the buffer nor the stack is empty
        if not conf.buffer or not conf.stack:
            return -1
        # Precondition: The word on top of the stack is not the root
        elif not conf.stack[-1]:
            return -1

        w_j = conf.buffer[0]
        w_i = conf.stack.pop()

        conf.arcs.append(Relation(w_j, relation, w_i))
        print("Left arc " + relation, conf.stack, conf.buffer, [str(arc) for arc in conf.arcs])

    @staticmethod
    def right_arc_star(conf, relation):
        """
        Add dependency relation (w_i, relation, w_j), reduce buffer
        :param conf: the current configuration, it has 3 elements: stack, buffer, arcs
        :param relation: the relation to be added
        """
        w_j = conf.buffer[0]
        w_i = conf.stack[-1]

        conf.buffer = conf.buffer[1:]
        conf.arcs.append(Relation(w_i, relation, w_j))
        print("Right arc star " + relation, conf.stack, conf.buffer, [str(arc) for arc in conf.arcs])


    @staticmethod
    def right_arc(conf, relation):
        """
        Add dependency relation (w_i, relation, w_j), append stack, reduce buffer
        :param conf: the current configuration, it has 3 elements: stack, buffer, arcs
        :param relation: the relation to be added
        """
        # Precondition: Neither the buffer nor the stack is empty
        if not conf.buffer or not conf.stack:
            return -1
        w_i = conf.stack[-1]
        w_j = conf.buffer[0]
        conf.stack.append(w_j)
        conf.buffer = conf.buffer[1:]
        conf.arcs.append(Relation(w_i, relation, w_j))
        print("Right arc " + relation, conf.stack, conf.buffer, [str(arc) for arc in conf.arcs])

    @staticmethod
    def shift(conf):
        """
        Push first element in buffer on to the stack
         :param conf: the current configuration, it has 3 elements: stack, buffer, arcs
        """

        conf.stack.append(conf.buffer[0])
        conf.buffer = conf.buffer[1:]
        print("Shift ", conf.stack, conf.buffer, [str(arc) for arc in conf.arcs])

    @staticmethod
    def reduce(conf):
        """
        Pop last element of the stack
        :param conf: the current configuration, it has 3 elements: stack, buffer, arcs
        """

        # Precondition: The last element must be independent on other words
        if conf.stack[-1] not in [ele.right for ele in conf.arcs]:
            return -1
        conf.stack.pop()
        print("Reduce ", conf.stack, conf.buffer, [str(arc) for arc in conf.arcs])

print(word_segmented_text)
# To do
# Create a file represent the relation between words
# Read the file
# Start doing arc
#
relations_set = []

with open('relations.txt', 'r') as file:
    for line in file:
        relate, left_val, right_val = line.split()
        relations_set.append(Relation(left_val, relate, right_val))


# Start parsing
def parsing():
    sentence_conf = Configuration(['root'], word_segmented_text, [])
    while 1:
        if len(sentence_conf.buffer) == 0:
            for arc in sentence_conf.arcs:
                print(arc)
            return sentence_conf
        # As of now, i should only consider on tail and head of these instance
        w_i = sentence_conf.stack[-1]
        w_j = sentence_conf.buffer[0]
        # Loop through all elements of the set to find relations
        right_rel = None
        left_rel = None
        for relation in relations_set:
            if Relation(w_i, "", w_j) == relation:
                # print("Found right")
                right_rel = relation
                # print(right_rel)
                break
            elif Relation(w_j, "", w_i) == relation:
                # print("Found left")
                left_rel = relation
                # print(left_rel)
                break
        # If there is no relation between tail and head, the buffer still have elements, shift
        if right_rel is None and left_rel is None:
            #We should check if w_j have some relation ship with some elements in stack, going down from tail, not including root
            have_hidden_arc = False
            for word in reversed(sentence_conf.stack[:-1]):
                for relation in relations_set:
                    if Relation(word, "", w_j) == relation:
                        # print("Have hidden arc")
                        have_hidden_arc = True
                        break
                    elif Relation(w_j, "", word) == relation:
                        # print("Have hidden arc")
                        have_hidden_arc = True
                        break
            if have_hidden_arc:
                # print("re")
                Transition.reduce(sentence_conf)
            else:
                # print("sh")
                Transition.shift(sentence_conf)
            # print(sentence_conf.stack)
            # print(sentence_conf.buffer)
        # If there is a relation between head and tail
        if right_rel is not None:
            # print("ri")
            # This part is to solve n - n modifier in Vietnamese
            if right_rel.relation_name == "nmod":
                Transition.right_arc_star(sentence_conf, right_rel.relation_name)
            else:
                Transition.right_arc(sentence_conf, right_rel.relation_name)
            # print(sentence_conf.stack)
            # print(sentence_conf.buffer)
        elif left_rel is not None:
            # print("le")
            Transition.left_arc(sentence_conf, left_rel.relation_name)
            # print(sentence_conf.stack)
            # print(sentence_conf.buffer)
        # If there are elements on stack but none in buffer, reduce
        # if len(sentence_conf.stack) > 1 and len(sentence_conf.buffer) == 0:
        #     print("re")
        #     Transition.reduce(sentence_conf)
        #     print(sentence_conf.stack)
        #     print(sentence_conf.buffer)

parsing()
