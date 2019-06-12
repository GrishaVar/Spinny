class Matrix():
    def __init__(self, *rows):
        self.value = tuple(tuple(x) for x in rows)
        self.n = len(rows)
        if self.n == 0:
            raise ValueError('Matrix of size zero')
        self.m = len(rows[0])
        for row in self.value:
            if len(row) == 0:
                raise ValueError('Matrix of size zero')
            if len(row) != self.m:
                raise ValueError('Marix with unequal row lengths')
    
    @property
    def size(self):
        return self.n, self.m

    def __repr__(self):
        res = ''
        for row in self.value:
            res += str(row) + '\n'
        return res
    
    def __add__(self, other):
        if not isinstance(other, Matrix):
            raise TypeError('Incompatible type: {}'.format(type(other)))
        if self.size != other.size:
            raise ValueError('Different Sizes')
        
        res = []
        for i in range(self.n):
            row = []
            for j in range(self.m):
                row.append(self.value[i][j] + other.value[i][j])
            res.append(row)
        return Matrix(*res)
    
    def __mul__(self, other):
        res = []
        if isinstance(other, Vector):
            return self * other.to_matrix()
        elif not isinstance(other, Matrix):  # Scalar Multiplication
            for i in range(self.n):
                row = []
                for j in range(self.m):
                    row.append(other * self.value[i][j])
                res.append(row)

        else:  # Matrix multiplication
            if self.m != other.n:
                raise ValueError('Incompatible Sizes')

            for i in range(self.n):
                row = []
                for j in range(other.m):
                    value = 0
                    for k in range(self.m):
                        value += self.value[i][k] * other.value[k][j]
                    row.append(value)
                res.append(row)

        return Matrix(*res)

    def __radd__(self, other):
        return self + other

    def __neg__(self):
        return self * -1

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return self - other

    def __rmul__(self, other):  # Matrix Mult isn't commutative but this only gets used when other isn't a Matrix
        return self * other
   
    def __pow__(self, other):
        res = self
        for x in range(other-1):
            res *= self
        return res
    
    def __rpow__(self, other):
        raise TypeError('???')
    
    @staticmethod
    def transpose(matr):
        return Matrix(*zip(*matr.value))


class Vector(Matrix):  # these are saved as horizontal but treated as vertical. Only difference is in __mul__ where value is transposed
    def __init__(self, *points):
        self.value = tuple(points)
        self.n = len(self.value)
        if self.n == 0:
            raise ValueError('Vector of size zero')
        self.m = 1
    
    def __repr__(self):
        return str(self.value) + 'ᵗ'

    def __add__(self, other):
        if not isinstance(other, Vector):
            raise TypeError('Incompatible type: {}'.format(type(other)))
        if self.size != other.size:
            raise ValueError('Different Sizes')

        res = Vector(map(sum, zip(self.value, other.value)))

    def __mul__(self, other):
        if isinstance(other, Matrix):
            return self.to_matrix() * other
        elif not isinstance(other, Vector):
            return Vector([other*a for a in self.value])
        else:
            if (1,1) == self.size == other.size:
                return Vector(self.value[0] * other.value[0])
            raise ValueError('Incompatible Sizes')

    def to_matrix(self):
        return Matrix(*zip(self.value))

