class Node:
    def __init__(self, value, next_node=None):
        self.value = value
        self.next = next_node

    def __repr__(self):
        return f"Node({self.value})"


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

    def append(self, value):
        new_node = Node(value)
        if not self.head:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def reverse(self):
        prev = None
        current = self.head
        self.tail = current 
        while current:
            next_node = current.next
            current.next = prev
            prev = current
            current = next_node
        self.head = prev

    def __repr__(self):
        nodes = []
        curr = self.head
        while curr:
            nodes.append(str(curr.value))
            curr = curr.next
        return " -> ".join(nodes) if nodes else "Empty List"


class Stack:
    def __init__(self):
        self.head = None

    def push(self, value):
        self.head = Node(value, self.head)

    def pop(self):
        if not self.head:
            raise IndexError("Попытка снять элемент с пустого стека.")
        val = self.head.value
        self.head = self.head.next
        return val

    def is_empty(self):
        return self.head is None

    def __repr__(self):
        nodes = []
        curr = self.head
        while curr:
            nodes.append(str(curr.value))
            curr = curr.next
        return " | ".join(nodes) if nodes else "Empty Stack"


class Queue:
    def __init__(self):
        self.head = None
        self.tail = None

    def enqueue(self, value):
        new_node = Node(value)
        if not self.tail:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node

    def dequeue(self):
        if not self.head:
            raise IndexError("Попытка извлечь элемент из пустой очереди.")
        val = self.head.value
        self.head = self.head.next
        if not self.head:
            self.tail = None
        return val

    def remove_by_id(self, req_id):
        curr = self.head
        prev = None
        
        while curr:
            if isinstance(curr.value, HashTable) and curr.value.get('номер') == req_id:
                if prev is None:  # Удаление из головы очереди
                    self.head = curr.next
                    if self.head is None:
                        self.tail = None
                else:  # Удаление из середины или хвоста очереди
                    prev.next = curr.next
                    if curr == self.tail:
                        self.tail = prev
                return True
            prev = curr
            curr = curr.next
        return False

    def is_empty(self):
        return self.head is None

    def __repr__(self):
        nodes = []
        curr = self.head
        while curr:
            if isinstance(curr.value, dict):
                nodes.append(str(curr.value.get('номер')))
            else:
                nodes.append(str(curr.value))
            curr = curr.next
        return " <- ".join(nodes) if nodes else "Empty Queue"


class HashTable:
    def __init__(self, capacity=37):
        self.capacity = capacity
        self.size = 0
        self._table = [LinkedList() for _ in range(self.capacity)]

    def _ensure_immutable(self, key):
        if isinstance(key, (list, dict, set)):
            return frozenset(key)
        return key

    def _hash(self, key):
        return abs(hash(key)) % self.capacity

    def put(self, key, value):
        immutable_key = self._ensure_immutable(key)
        index = self._hash(immutable_key)
        bucket = self._table[index]  

        curr = bucket.head
        while curr:
            k, v = curr.value
            if k == immutable_key:
                curr.value = (immutable_key, value) 
                return
            curr = curr.next

        bucket.append((immutable_key, value))
        self.size += 1

    def get(self, key):
        immutable_key = self._ensure_immutable(key)
        index = self._hash(immutable_key)
        bucket = self._table[index]

        curr = bucket.head
        while curr:
            k, v = curr.value
            if k == immutable_key:
                return v
            curr = curr.next
        return None

    def remove(self, key):
        immutable_key = self._ensure_immutable(key)
        index = self._hash(immutable_key)
        bucket = self._table[index]

        curr = bucket.head
        prev = None

        while curr:
            k, v = curr.value
            if k == immutable_key:
                if prev is None: 
                    bucket.head = curr.next
                    if bucket.head is None:
                        bucket.tail = None
                else: 
                    prev.next = curr.next
                    if curr == bucket.tail:
                        bucket.tail = prev
                self.size -= 1
                return True
            prev = curr
            curr = curr.next
        return False

    def __repr__(self):
        items = []
        for i in range(self.capacity):
            curr = self._table[i].head
            while curr:
                k, v = curr.value
                items.append(f"{k}: {v!r}")
                curr = curr.next

        if items:
            return "{" + ", ".join(items) + "}\n"
        return "{}\n"
