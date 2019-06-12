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
        res_parts = []
        for row in self.value:
            res_parts.append('\t'.join(map(str, row)))
        res = ')\n('.join(res_parts)
        return '(' + res + ')'
    
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
        if not isinstance(other, Matrix):  # Scalar Multiplication
            for i in range(self.n):
                row = []
                for j in range(self.m):
                    row.append(other * self.value[i][j])
                res.append(row)

        else:  # Matrix multiplication. m*m=m  v*m=m  m*v=v
            if self.m != other.n:
                raise ValueError('Incompatible Sizes')

            if isinstance(other, Vector):
                return (self * other.to_matrix()).to_vector()

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
    
    def to_vector(self):
        if self.m != 1:
            return ValueError('Not a vector')
        return Vector(*Matrix.transpose(self).value[0])

    def copy(self):
        return Matrix(*(self.value[:]))


class Vector(Matrix):  # these are saved as horizontal but treated as vertical.
    def __init__(self, *points):
        self.value = tuple(points)
        self.n = len(self.value)
        if self.n == 0:
            raise ValueError('Vector of size zero')
        self.m = 1
    
    def __repr__(self):
        return '(' + (', '.join(map(str, self.value))) + ')ᵗ'

    def __add__(self, other):
        if not isinstance(other, Vector):
            raise TypeError('Incompatible type: {}'.format(type(other)))
        if self.size != other.size:
            raise ValueError('Different Sizes')
        return Vector(*map(sum, zip(self.value, other.value)))

    def __mul__(self, other):
        if not isinstance(other, Matrix):
            return Vector(*[other*a for a in self.value])
        else:   # Matrix multiplication. v*m=m  m*v=v  v*v=v
            if self.m != other.n:
                raise ValueError('Incompatible Sizes')
            if not isinstance(other, Vector):
                return self.to_matrix() * other
            else:  # only possible if n=m=1 for both. I doubt this will ever be used.
                return Vector(self.value[0] * other.value[0])

    def to_matrix(self):
        return Matrix(*zip(self.value))

    def copy(self):
        return Vector(*self.value)

