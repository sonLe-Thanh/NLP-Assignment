from vncorenlp import VnCoreNLP
import os

pathToJar = "../Assignment/VnCoreNLP-1.1.1.jar"
annotator = VnCoreNLP(pathToJar, annotators="wseg", max_heap_size='-Xmx2g')


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


class Token():
    def __init__(self, word, type):
        self.type = type
        self.word = word
        self.children = []

    def add(self, node_to_add):
        self.children.append(node_to_add)

    def __str__(self):
        if self.children:
            if "-from" in self.word:
                return "{} [{}]".format(self.type + " " + self.word[:-5],
                                        ", ".join(str(c) for c in self.children if str(c) != ""))
            elif "-to" in self.word:
                return "{} [{}]".format(self.type + " " + self.word[:-3],
                                        ", ".join(str(c) for c in self.children if str(c) != ""))
            else:
                return "{} [{}]".format(self.type + " " + self.word,
                                        ", ".join(str(c) for c in self.children if str(c) != ""))
        else:
            if self.type != "<none>":
                if "-from" in self.word:
                    return "{}".format(self.type + " " + self.word[:-5])
                elif "-to" in self.word:
                    return "{}".format(self.type + " " + self.word[:-3])
                else:
                    return "{}".format(self.type + " " + self.word)
            else:
                return ""


class Transition:

    @staticmethod
    def left_arc(conf, relation, file=None):
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
        print(
            f"{'Left arc ' + relation:<25}  {'[' + ', '.join(item for item in conf.stack) + ']':<40} {'[' + ', '.join(item for item in conf.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in conf.arcs) + ']'}",
            file=file)

    @staticmethod
    def right_arc_star(conf, relation, file=None):
        """
        Add dependency relation (w_i, relation, w_j), reduce buffer
        :param conf: the current configuration, it has 3 elements: stack, buffer, arcs
        :param relation: the relation to be added
        """
        w_j = conf.buffer[0]
        w_i = conf.stack[-1]

        conf.buffer = conf.buffer[1:]
        conf.arcs.append(Relation(w_i, relation, w_j))
        print(
            f"{'Right arc star ' + relation:<25}  {'[' + ', '.join(item for item in conf.stack) + ']':<40} {'[' + ', '.join(item for item in conf.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in conf.arcs) + ']'}",
            file=file)
        # print("Right arc star " + relation, conf.stack, conf.buffer, [str(arc) for arc in conf.arcs],sep="\t\t\t", file=file)

    @staticmethod
    def right_arc(conf, relation, file=None):
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
        print(
            f"{'Right arc ' + relation:<25}  {'[' + ', '.join(item for item in conf.stack) + ']':<40} {'[' + ', '.join(item for item in conf.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in conf.arcs) + ']'}",
            file=file)
        # print("Right arc " + relation, conf.stack, conf.buffer, [str(arc) for arc in conf.arcs],sep="\t\t\t", file=file)

    @staticmethod
    def shift(conf, file=None):
        """
        Push first element in buffer on to the stack
         :param conf: the current configuration, it has 3 elements: stack, buffer, arcs
        """

        conf.stack.append(conf.buffer[0])
        conf.buffer = conf.buffer[1:]
        print(
            f"{'Shift ':<25}  {'[' + ', '.join(item for item in conf.stack) + ']':<40} {'[' + ', '.join(item for item in conf.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in conf.arcs) + ']'}",
            file=file)
        # print("Shift ", conf.stack, conf.buffer, [str(arc) for arc in conf.arcs],sep="\t\t\t",file=file)

    @staticmethod
    def reduce(conf, file=None):
        """
        Pop last element of the stack
        :param conf: the current configuration, it has 3 elements: stack, buffer, arcs
        """

        # Precondition: The last element must be independent on other words
        if conf.stack[-1] not in [ele.right for ele in conf.arcs]:
            return -1
        conf.stack.pop()
        print(
            f"{'Reduce ':<25}  {'[' + ', '.join(item for item in conf.stack) + ']':<40} {'[' + ', '.join(item for item in conf.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in conf.arcs) + ']'}",
            file=file)
        # print("Reduce ", conf.stack, conf.buffer, [str(arc) for arc in conf.arcs],sep="\t\t\t",file=file)


def city_name_encode(city_name):
    if city_name == "hồ_chí_minh":
        return "HCMC"
    elif city_name == "hà_nội":
        return "HN"
    elif city_name == "đà_nẵng":
        return "DANANG"
    elif city_name == "huế":
        return "HUE"


class ProcessText:

    @staticmethod
    def preprocessing(text):
        text = text.lower()
        word_segmented_text = annotator.tokenize(text)
        word_segmented_text = word_segmented_text[0]
        # Check if given sentences have a real main verb
        # First read the dictionary
        dictionary_set = {}
        with open('../Assignment/Models/dictionary.txt', 'r') as file:
            for line in file:
                word, type_word = line.split()
                dictionary_set.setdefault(word, type_word)

        def isHaveVerb(text_list):
            for check_word in text_list:
                if check_word in dictionary_set:
                    if dictionary_set[check_word] == "V":
                        return True
            return False

        def getFistPrepIdx(text_list):
            for i in range(len(text_list)):
                if text_list[i] in dictionary_set:
                    if dictionary_set[text_list[i]] == "P":
                        return i
            return -1

        def addRealVerb(text_list):
            if not isHaveVerb(text_list):
                idx_to_add = getFistPrepIdx(text_list)
                text_list.insert(idx_to_add, "đi")

        addRealVerb(word_segmented_text)
        # remove useless "thành phố" verb which may cause trouble parsing
        word_segmented_text = [x for x in word_segmented_text if x != 'thành_phố']
        return word_segmented_text

    @staticmethod
    def parsing(word_segmented_text):
        relations_set = []
        city_set = []
        connected_arc = {'từ': 0, 'đến': 0}

        with open('../Assignment/Models/relations.txt', 'r') as file1:
            for line1 in file1:
                relate, left_val, right_val = line1.split()
                relations_set.append(Relation(left_val, relate, right_val))

        with open('../Assignment/Models/city.txt', 'r') as file2:
            city_set = file2.read().splitlines()

        file_parsing = open("../Assignment/Output/output_a.txt", 'a')

        file_arcs = open("../Assignment/Output/output_b.txt", 'a')
        # print(city_set)
        print(
            f"{'ACTION ':<25}  {'STACK':<40} {'BUFFER':<100} {'ARCS'}",
            file=file_parsing)
        sentence_conf = Configuration(['root'], word_segmented_text, [])
        print(
            f"{'':<25}  {'[' + ', '.join(item for item in sentence_conf.stack) + ']':<40} {'[' + ', '.join(item for item in sentence_conf.buffer) + ']':<100} {'[' + ', '.join(str(arc) for arc in sentence_conf.arcs) + ']'}",
            file=file_parsing)
        while 1:
            # Begin parsing
            # print("Tesdfsssssst", file=file_parsing)
            if len(sentence_conf.buffer) == 0:
                print("\n", file=file_parsing)
                print(", ".join(str(arc) for arc in sentence_conf.arcs) + "\n", file=file_arcs)
                # for arc in sentence_conf.arcs:
                #     print(arc)
                return sentence_conf.arcs
            # As of now, i should only consider on tail and head of these instance
            w_i = sentence_conf.stack[-1]
            w_j = sentence_conf.buffer[0]
            # print(w_i)
            # print(w_j)
            # Loop through all elements of the set to find relations
            right_rel = None
            left_rel = None
            for relation in relations_set:
                if Relation(w_i, "", w_j) == relation:
                    # print("Found right")
                    right_rel = relation
                    if w_i in city_set or w_i == "lúc" and w_j in ["từ", "đến"]:
                        right_rel = None
                    if right_rel is not None:
                        if w_i in ['từ', 'đến']:
                            connected_arc[w_i] += 1
                    # print(connected_arc)
                    # print(right_rel)
                    break
                elif Relation(w_j, "", w_i) == relation:
                    # print("Found left")
                    left_rel = relation
                    # Exclude cases that this somewhat parsing the wrong order
                    # The order is like <from> <at> <to> <at>
                    if w_i in city_set or w_i == "lúc" and w_j in ["từ", "đến"]:
                        left_rel = None
                    if left_rel is not None:
                        if w_j in ['từ', 'đến']:
                            connected_arc[w_j] += 1
                    # print(connected_arc)
                    # print(left_rel)
                    break
            # If there is no relation between tail and head, the buffer still have elements, shift
            if right_rel is None and left_rel is None:
                # We should check if w_j have some relation ship with some elements in stack, going down from tail,
                # not including root
                have_hidden_arc = False
                for word in reversed(sentence_conf.stack[:-1]):
                    for relation in relations_set:
                        if Relation(word, "", w_j) == relation:
                            # print("Have hidden arc")
                            have_hidden_arc = True
                            # Check if the relation is already featured in the arcs
                            for featured in sentence_conf.arcs:
                                if Relation(word, "", w_j) == featured:
                                    have_hidden_arc = False
                            # I think most P should only have 2 connected arcs at most
                            if word in ['từ', 'đến']:
                                if connected_arc[word] >= 2:
                                    have_hidden_arc = False
                            break
                        elif Relation(w_j, "", word) == relation:
                            # print("Have hidden arc")
                            have_hidden_arc = True
                            for featured in sentence_conf.arcs:
                                if Relation(w_j, "", word) == featured:
                                    have_hidden_arc = False
                            if w_j in ['từ', 'đến']:
                                if connected_arc[w_j] >= 2:
                                    have_hidden_arc = False
                            break
                if have_hidden_arc:
                    # print("re")
                    Transition.reduce(sentence_conf, file_parsing)
                else:
                    # print("sh")
                    Transition.shift(sentence_conf, file_parsing)
                # print(sentence_conf.stack)
                # print(sentence_conf.buffer)
            # If there is a relation between head and tail
            if right_rel is not None:
                # print("ri")
                # This part is to solve N - N modifier in Vietnamese
                if right_rel.relation_name == "nmod":
                    Transition.right_arc_star(sentence_conf, right_rel.relation_name, file_parsing)
                else:
                    Transition.right_arc(sentence_conf, right_rel.relation_name, file_parsing)
                # print(sentence_conf.stack)
                # print(sentence_conf.buffer)
            elif left_rel is not None:
                # print("le")
                Transition.left_arc(sentence_conf, left_rel.relation_name, file_parsing)
                # print(sentence_conf.stack)
                # print(sentence_conf.buffer)
            # If there are elements on stack but none in buffer, reduce
            # if len(sentence_conf.stack) > 1 and len(sentence_conf.buffer) == 0:
            #     print("re")
            #     Transition.reduce(sentence_conf)
            #     print(sentence_conf.stack)
            #     print(sentence_conf.buffer)

    @staticmethod
    def grammar_relation(sentence_conf):
        # Create a grammar tree represent the grammatical relation of the sentence
        tree = {}
        parent_node = child_node = None
        name_parent = name_child = None

        for idx, rel in enumerate(sentence_conf):
            if rel.relation_name == "root":
                name_parent = rel.left
                name_child = rel.right
                parent_node = Token(name_parent, "S")
                child_node = Token(name_child, "V")
            elif rel.relation_name == "punc":
                # continue
                name_parent = rel.left
                name_child = rel.right
                parent_node = Token(name_parent, "V")
                child_node = Token(name_child, "<none>")
            elif rel.relation_name == "nmod":
                name_parent = rel.left
                name_child = rel.right
                parent_node = Token(name_parent, "N")
                child_node = Token(name_child, "N")
            elif rel.relation_name in ["nsubj", "dobj"]:
                name_parent = rel.left
                name_child = rel.right
                parent_node = Token(name_parent, "V")
                child_node = Token(name_child, "N")
            elif rel.relation_name == "prep":
                name_parent = rel.left
                if rel.left == "đến":
                    name_child = rel.right + "-to"
                elif rel.left == "từ":
                    name_child = rel.right + "-from"
                parent_node = Token(name_parent, "V")
                child_node = Token(name_child, "P")
            elif rel.relation_name == "tmod":
                # get the closest prep, it's before the current relation
                name_child = rel.right
                if sentence_conf[idx - 1].left == "đến":
                    name_parent = rel.left + "-to"
                elif sentence_conf[idx - 1].left == "từ":
                    name_parent = rel.left + "-from"
                parent_node = Token(name_parent, "P")
                child_node = Token(name_child, "N")
            elif rel.relation_name == "pobj":
                name_parent = rel.left
                name_child = rel.right
                parent_node = Token(name_parent, "V")
                child_node = Token(name_child, "P")

            tree.setdefault(name_parent, parent_node)
            tree.setdefault(name_child, child_node)
            tree[name_parent].add(tree[name_child])

        # Write these to files

        file_grammar_relation = open("../Assignment/Output/output_c.txt", 'a')
        print("S root [", file=file_grammar_relation)
        print("SUBJ [" + str(tree["root"].children[0].children[0]) + "]", file=file_grammar_relation)
        print("[MAIN-" + tree["root"].children[0].type + " " + tree["root"].children[0].word + "]",
              file=file_grammar_relation)
        for i in range(1, len(tree["root"].children[0].children)):
            if str(tree["root"].children[0].children[i]) != "":
                print("[" + str(tree["root"].children[0].children[i]) + "]", file=file_grammar_relation)
        print("]", file=file_grammar_relation)
        ##
        return tree["root"].children[0]

    @staticmethod
    def logical_form(grammar_relation):
        # Change to logical form
        # print(grammar_relation.word)
        question_type = ["WH-QUERY", "Y/N-QUESTION", "COMMAND"]
        city_set = []
        bus_name = []
        with open('../Assignment/Models/city.txt', 'r') as file1:
            city_set = file1.read().splitlines()
        with open('../Assignment/Models/BusName.txt', 'r') as file2:
            bus_name = file2.read().splitlines()

        # Atm, should only concern on WH
        log_form = {}
        log_form.setdefault(question_type[0], {})
        log_form[question_type[0]].setdefault(grammar_relation.word, {})
        agent = from_loc = to_loc = from_time = to_time = ""

        for info in grammar_relation.children:
            if info.word == "xe_buýt":
                agent += "<TRAIN t1 "
                if info.children:
                    for child_subj in info.children:
                        if child_subj.word == "nào":
                            agent += "<WH t1 NAME>"
                        elif child_subj.word in bus_name:
                            agent += "<NAME t1 \"" + child_subj.word + "\">"
                agent += ">"
            elif info.word == "từ":
                # If have children
                if info.children:
                    for child in info.children:
                        # if this child is a place -> city name:
                        if child.type == "N":
                            if child.word in city_set:
                                from_loc += "<CITY t1<NAME t1 " + child.word + ">>"
                        # if this child is a preposition -> time
                        if child.type == "P":
                            if child.word == "lúc-from":
                                # get the time
                                from_time += "<TIME t1 " + child.children[0].word + ">"
            elif info.word == "đến":
                # If have children
                if info.children:
                    for child in info.children:
                        # if this child is a place -> city name:
                        if child.type == "N":
                            if child.word in city_set:
                                to_loc += "<CITY t1<NAME t1 " + child.word + ">>"
                        # if this child is a preposition -> time
                        if child.type == "P":
                            if child.word == "lúc-to":
                                # get the time
                                to_time += "<TIME t1 " + child.children[0].word + ">"

        if agent != "":
            log_form[question_type[0]][grammar_relation.word].setdefault("AGENT", agent)
        if from_loc != "":
            log_form[question_type[0]][grammar_relation.word].setdefault("SOURCE", from_loc)
        if from_time != "":
            log_form[question_type[0]][grammar_relation.word].setdefault("LEAVE", from_time)
        if to_loc != "":
            log_form[question_type[0]][grammar_relation.word].setdefault("DESTINATION", to_loc)
        if to_time != "":
            log_form[question_type[0]][grammar_relation.word].setdefault("ARRIVE", to_time)


        file_logical_form = open("../Assignment/Output/output_d.txt", 'a')
        print(log_form, file=file_logical_form)

        return log_form

    @staticmethod
    def procedure_form(logical_form):
        # Change logical_form (as a dict) to procedure form
        # print(logical_form)
        procedure_str = ""
        if "WH-QUERY" in logical_form:
            # print("HI")
            procedure_str += "PRINT-ALL\n"
            # at this point, only one verb allow:
            if "đi" in logical_form["WH-QUERY"]:
                info_dict = logical_form["WH-QUERY"]["đi"]
                # print(info_dict)
                # Get as much info as possible:
                agent_query = source_query = dest_query = leave_query = arrive_query = ""
                for idx, key in enumerate(info_dict):
                    if key == "AGENT":
                        # agent_query = ""
                        # Processing agent
                        agent_info = info_dict[key][:-2].split("<")[1:]
                        if "WH" in agent_info[1]:
                            # Unknown train name
                            agent_query += "?tr (TRAIN ?tr) "
                        elif "NAME" in agent_info[1]:
                            train_name = agent_info[1].split()[2][1:-1].upper()
                            agent_query += "(TRAIN " + train_name + ") "
                        # print(agent_query)
                    elif key == "SOURCE":
                        # source_query = ""
                        source_info = info_dict[key][:-2].split("<")[1:]
                        # print(source_info)
                        if "WH" in source_info[1]:
                            # Unknow city name
                            source_query += "?dp (DTIME ?tr ?p ?dt)"
                        else:
                            encoded_city_name = city_name_encode(source_info[1].split()[2])
                            source_query += "(DTIME ?tr " + encoded_city_name + " ?dt) "
                    elif key == "DESTINATION":
                        # dest_query = ""
                        dest_info = info_dict[key][:-2].split("<")[1:]
                        # print(dest_info)
                        if "WH" in dest_info[1]:
                            # Unknow city name
                            dest_query += "?ap (ATIME ?tr ?p ?at)"
                        else:
                            encoded_city_name = city_name_encode(dest_info[1].split()[2])
                            dest_query += "(ATIME ?tr " + encoded_city_name + " ?at) "
                    elif key == "LEAVE":
                        # leave_query = ""
                        leave_info = info_dict[key][1:-1].split()
                        if "WH" in leave_info[2]:
                            leave_query += "?dt (DTIME ?tr ?p ?dt)"
                        else:
                            # print(leave_info[2].split())
                            leave_time = leave_info[2].split()[0] + "HR"
                            leave_query += "(DTIME ?tr ?p " + leave_time + ")"
                    elif key == "ARRIVE":
                        # arrive_query = ""
                        arrive_info = info_dict[key][1:-1].split()
                        if "WH" in arrive_info[2]:
                            arrive_query += "(ATIME ?tr ?p ?at)"
                        else:
                            leave_time = arrive_info[2].split()[0] + "HR"
                            arrive_query += "(ATIME ?tr ?p " + leave_time + ")"
                # print(agent_query, source_query, dest_query, leave_query, arrive_query)
                # Combine the query to get a full query
                full_source_query = full_leave_query = ""
                if source_query == "" and leave_query != "":
                    full_source_query = leave_query
                elif source_query != "" and leave_query == "":
                    full_source_query = source_query
                elif source_query == "" and leave_query == "":
                    full_source_query = ""
                else:
                    # Get the ?info data
                    question_mark = []
                    dplace_info = "?p"
                    dtime_info = "?dt"
                    split_source = source_query.split()
                    split_leave = leave_query.split()
                    if "?" in split_source[0]:
                        question_mark.append(split_source[0])
                        if "?" not in split_source[3]:
                            dplace_info = split_source[3]
                        if "?" not in split_source[4]:
                            dtime_info = split_source[4]
                    else:
                        if "?" not in split_source[2]:
                            dplace_info = split_source[2]
                        if "?" not in split_source[3]:
                            dtime_info = split_source[3]
                    if "?" in split_leave[0]:
                        question_mark.append(split_leave[0])
                        if "?" not in split_leave[3]:
                            dplace_info = split_leave[3]
                        if "?" not in split_leave[4]:
                            dtime_info = split_leave[4]
                    else:
                        if "?" not in split_leave[2]:
                            dplace_info = split_leave[2]
                        if "?" not in split_leave[3]:
                            dtime_info = split_leave[3]
                    full_source_query = " ".join(
                        x for x in question_mark) + " (DTIME ?tr " + dplace_info + " " + dtime_info
                    # print(full_source_query)
                    # print(split_source, split_leave)

                if dest_query == "" and arrive_query != "":
                    full_leave_query = arrive_query
                elif dest_query != "" and arrive_query == "":
                    full_leave_query = dest_query
                elif dest_query == "" and arrive_query == "":
                    full_leave_query = ""
                else:
                    # Get the ?info data
                    question_mark = []
                    aplace_info = "?p"
                    atime_info = "?at"
                    split_dest = dest_query.split()
                    split_arrive = arrive_query.split()
                    if "?" in split_dest[0]:
                        question_mark.append(split_dest[0])
                        if "?" not in split_dest[3]:
                            aplace_info = split_dest[3]
                        if "?" not in split_dest[4]:
                            atime_info = split_dest[4]
                    else:
                        if "?" not in split_dest[2]:
                            aplace_info = split_dest[2]
                        if "?" not in split_dest[3]:
                            atime_info = split_dest[3]
                    if "?" in split_arrive[0]:
                        question_mark.append(split_arrive[0])
                        if "?" not in split_arrive[3]:
                            aplace_info = split_arrive[3]
                        if "?" not in split_arrive[4]:
                            atime_info = split_arrive[4]
                    else:
                        if "?" not in split_arrive[2]:
                            aplace_info = split_arrive[2]
                        if "?" not in split_arrive[3]:
                            atime_info = split_arrive[3]
                    full_leave_query = " ".join(
                        x for x in question_mark) + " (ATIME ?tr " + aplace_info + " " + atime_info
                    # print(full_leave_query)
                    # print(split_arrive, split_dest)
                if agent_query != "":
                    procedure_str += agent_query + "\n"
                if full_source_query != "":
                    procedure_str += full_source_query + "\n"
                if full_leave_query != "":
                    procedure_str += full_leave_query + "\n"


                file_procedure_form = open("../Assignment/Output/output_e.txt", 'a')
                print(procedure_str, file=file_procedure_form)
                return procedure_str

    @staticmethod
    def get_query_answer(query):
        # read data
        train_data = []
        atime_data = []
        dtime_data = []
        rtime_data = []
        with open('../Assignment/Models/data.txt', 'r') as file:
            lines = [line.rstrip() for line in file]
            for line in lines:
                if "TRAIN" in line:
                    train_data.append(line)
                elif "ATIME" in line:
                    atime_data.append(line)
                elif "DTIME" in line:
                    dtime_data.append(line)
                elif "RUN-TIME" in line:
                    rtime_data.append(line)
        commands = query.split("\n")
        # Extract bus name, city name, hour from the given data
        possible_train_name = [item[1:-1].split()[1] for item in train_data]
        possible_city_code = ['HCMC', 'HN', 'DANANG', 'HUE']
        possible_atimes = [item[1:-1].split()[3] for item in atime_data]
        possible_dtimes = [item[1:-1].split()[3] for item in dtime_data]
        possible_time = list(set(possible_atimes) | set(possible_dtimes))
        # print(commands)
        result = []
        if commands[0] == "PRINT-ALL":
            # start matching
            var_to_get = []
            gotten_train = []
            gotten_dp = []
            gotten_dt = []
            gotten_ap = []
            gotten_at = []
            result_d = []
            result_a = []
            dtime_appear = False
            atime_appear = False
            # print(commands)
            for item in commands[1:]:
                if item != "":
                    # print(item.split()[0])
                    if "?" in item.split()[0]:
                        if item.split()[0] == "?tr":
                            # Train name
                            var_to_get.append(item.split()[0])
                            for train_item in train_data:
                                gotten_train.append(train_item.split()[1][:-1])
                        if item.split()[0] == "?dp":
                            # dname
                            continue
                    else:
                        if gotten_train:
                            for train_name in gotten_train:
                                # Replace ?tr in 2 command by train_name
                                check_cmd = item.replace("?tr", train_name).strip()
                                have_mark_unused = False
                                unused_part = ""
                                # Check dtime condition
                                if "DTIME" in check_cmd:
                                    dtime_appear = True
                                    # print(check_cmd)

                                    # Check if there is ? in the command
                                    # Remove the parenthesis
                                    parts_check_cmd = check_cmd[1:-1].split()
                                    for part in parts_check_cmd:
                                        if "?" in part:
                                            # Check if not part is in var_to_get
                                            if not part in var_to_get:
                                                have_mark_unused = True
                                                unused_part = part
                                                break
                                    if have_mark_unused:
                                        # Don't care this in the command -> Make it available for all possible values
                                        if unused_part == "?dp":
                                            for citi in possible_city_code:
                                                check_cmd = item.replace("?dp", citi).replace("?tr", train_name).strip()
                                                if check_cmd in dtime_data:
                                                    result_d.append(train_name)
                                        elif unused_part == "?dt":
                                            for time_point in possible_time:
                                                check_cmd = item.replace("?dt", time_point).replace("?tr", train_name).strip()
                                                if check_cmd in dtime_data:
                                                        result_d.append(train_name)
                                    else:
                                        if check_cmd in dtime_data:
                                            result_d.append(train_name)
                                elif "ATIME" in check_cmd:
                                    # print(check_cmd)
                                    atime_appear = True
                                    parts_check_cmd = check_cmd[1:-1].split()
                                    for part in parts_check_cmd:
                                        if "?" in part:
                                            # Check if not part is in var_to_get
                                            if not part in var_to_get:
                                                have_mark_unused = True
                                                unused_part = part
                                                break
                                    if have_mark_unused:
                                        # print(unused_part)
                                        # Don't care this in the command -> Make it available for all possible values
                                        if unused_part == "?ap":
                                            for citi in possible_city_code:
                                                check_cmd = item.replace("?ap", citi).replace("?tr", train_name).strip()
                                                if check_cmd in atime_data:
                                                    result_a.append(train_name)
                                        elif unused_part == "?at":
                                            for time_point in possible_time:
                                                check_cmd = item.replace("?at", time_point).replace("?tr", train_name).strip()
                                                # print(check_cmd)
                                                if check_cmd in atime_data:
                                                    result_a.append(train_name)
                                    else:
                                        if check_cmd in atime_data:
                                            result_a.append(train_name)
            # print(result_a)
            # print(result_d)
            if dtime_appear and atime_appear:
                result = list(set(result_a) & set(result_d))
            elif not dtime_appear and atime_appear:
                result = result_a
            elif dtime_appear and not atime_appear:
                result = result_d
            # print(result)
        #         print(item.split())
        # print(train_data)
        # print(atime_data)
        # print(dtime_data)
        # print(rtime_data)
        result_str = ""
        if result:
            result_str += "Kết quả là " + ",".join(res for res in result)
        else:
            result_str += "Không có kết quả thoả mãn"

        file_result = open("../Assignment/Output/output_f.txt", 'a')
        print(result_str, file=file_result)
        return result_str


def process(text):
    preprocessed_text = ProcessText.preprocessing(text)
    word_relation = ProcessText.parsing(preprocessed_text)
    grammar_rel = ProcessText.grammar_relation(word_relation)
    log_form = ProcessText.logical_form(grammar_rel)
    query_str = ProcessText.procedure_form(log_form)
    answer = ProcessText.get_query_answer(query_str)
    return answer


# text = "Xe buýt nào từ Đà Nẵng lúc 8:30 HR đến thành phố Hồ Chí Minh lúc 18:30 HR?"
# print(process(text))
