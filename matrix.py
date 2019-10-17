from math import sqrt


class Matrix:
    """
    Matrix implementation.

    Supports addition (+), subtraction (-),
    negation (-m), multiplication (scalar, matrix) (*),
    powers (**).

    det(self) returns determinant (memoised).
    transpose(m) returns m transposed.
    row_switch(self, i, j) elementary row operation swap.
    row_mult(self, i, m) elementary row operation multiply.
    row_add(self, i, j, m) elementary row operation add.

    value: tuple of values.
    n: number of rows.
    m: number of columns.
    """
    def __init__(self, *rows):
        self.value = tuple(map(tuple, rows))
        self.n = len(rows)
        if self.n == 0:
            raise ValueError('Matrix of size zero')
        self.m = len(rows[0])
        for row in self.value:
            if len(row) == 0:
                raise ValueError('Matrix of size zero')
            if len(row) != self.m:
                raise ValueError('Matrix with unequal row lengths')
        self._det = None

    @property
    def size(self):
        return self.n, self.m

    @property
    def det(self):
        """
        Calculate and store determinant.
        :return: int
        """
        if self._det is None:  # kinda-sorta-memoised determinant
            if self.n != self.m:
                self._det = 0
            elif self.n == 1:
                self._det = self.value[0][0]
            elif self.n == 2:
                v = self.value
                self._det = v[0][0]*v[1][1] - v[0][1]*v[1][0]
            elif self.n == 3:
                v = self.value
                self._det = (
                    v[0][0]*v[1][1]*v[2][2] +
                    v[0][1]*v[1][2]*v[2][0] +
                    v[0][2]*v[1][0]*v[2][1] -
                    v[0][2]*v[1][1]*v[2][0] -
                    v[0][1]*v[1][0]*v[2][2] -
                    v[0][0]*v[1][2]*v[2][1]
                )  # I regret this
            else:
                raise NotImplementedError('oof dude')
        return self._det

    def __repr__(self):
        res_parts = []
        for row in self.value:
            res_parts.append('\t'.join(map(str, row)))
        res = ')\n('.join(res_parts)
        return '(' + res + ')'

    def __add__(self, other):
        if isinstance(other, int) and other == 0:
            return self
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
        """Scalar and matrix multiplication."""
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

    def __eq__(self, other):
        return isinstance(other, Matrix) and self.value == other.value

    @staticmethod
    def transpose(m):
        return Matrix(*zip(*m.value))

    def to_vector(self):
        """
        Converts single-column matrix into a vector.
        :return: Vector
        """
        if self.m != 1:
            return ValueError('Not a vector')
        return Vector(*Matrix.transpose(self).value[0])

    def copy(self):
        return Matrix(*self.value)

    def row_switch(self, i, j):
        """
        Swap row positions.
        :param i: index of row 1
        :param j: index of row 2
        """
        value = list(self.value)
        temp = value[j]
        value[j] = value[i]
        value[i] = temp
        self.value = tuple(value)

    def row_mult(self, i, m):
        """
        Multiply a row by a scalar.
        :param i: index of row
        :param m: non-zero scalar
        """
        if m == 0:
            raise ValueError("m can't be zero!")
        value = list(self.value)
        value[i] = tuple(m*x for x in value[i])
        self.value = tuple(value)

    def row_add(self, i, j, m):
        """
        Add a row to another (with scaling).
        :param i: index of row to be changed
        :param j: index of row to add
        :param m: non-zero scalar
        :return:
        """
        if m == 0:
            raise ValueError("m can't be zero!")
        value = list(self.value)
        row = tuple(m*x for x in value[j])
        value[i] = tuple(x+y for x,y in zip(value[i], row))
        self.value = tuple(value)


class Vector(Matrix):  # these are saved as horizontal but treated as vertical.
    """
    Subclass of Matrix for single-column matrices.

    length(self) returns euclidean norm (memoised).
    dot(self, other) returns dot product.
    cross(self, other) return cross product.
    project(self, basis) return projection onto basis.

    value: tuple of values.
    n: int, number of entries.
    m: int, 1.
    """
    def __init__(self, *points):
        self.value = tuple(points)
        self.n = len(self.value)
        if self.n == 0:
            raise ValueError('Vector of size zero')
        self.m = 1
        self._length = None

    def __repr__(self):
        return '(' + (', '.join(str(x) for x in self.value)) + ')ᵗ'  # add rounding

    def __add__(self, other):
        if isinstance(other, int) and other == 0:  # allows sum()
            return self
        if not isinstance(other, Vector):
            raise TypeError('Incompatible type: {}'.format(type(other)))
        if self.size != other.size:
            raise ValueError('Different Sizes')
        return Vector(*map(sum, zip(self.value, other.value)))

    def __mul__(self, other):
        if not isinstance(other, Matrix):
            return Vector(*(other*a for a in self.value))
        else:   # Matrix multiplication. v*m=m  m*v=v  v*v=v
            if self.m != other.n:
                raise ValueError('Incompatible Sizes')
            if not isinstance(other, Vector):
                return self.to_matrix() * other
            else:  # only possible if n=m=1 for both. I doubt this will ever be used.
                return Vector(self.value[0] * other.value[0])

    @property
    def length(self):  # another semi-memoised expensive function
        """
        Returns euclidean norm of vector.
        :return: int
        """
        if self._length is None:
            self._length = sqrt(sum([c**2 for c in self.value]))
        return self._length

    def to_matrix(self):
        """Converts Vector to Matrix."""
        return Matrix(*zip(self.value))

    def copy(self):
        return Vector(*self.value)

    def dot(self, other):
        """
        Dot Product.
        :param other: Vector
        :return: self·other
        """
        if not isinstance(other, Vector):
            raise TypeError('Incompatible type: {}'.format(type(other)))
        turned = Matrix.transpose(self.to_matrix())
        return (turned*other).value[0]  # matrix only has one element

    def cross(self, other):
        """
        Cross Product. Only defined for 3 dimensional vectors.
        :param other: Vector
        :return: self⨯other
        """
        if not isinstance(other, Vector):
            raise TypeError('Incompatible type: {}'.format(type(other)))
        if self.n != other.n:
            raise ValueError('Incompatible Sizes')
        if self.n != 3:  # Also exists for 7 dimentions... implement?
            raise ValueError('Non-3 dimention')

        a1, a2, a3 = self.value
        b1, b2, b3 = other.value

        s1 = a2 * b3 - a3 * b2
        s2 = a3 * b1 - a1 * b3
        s3 = a1 * b2 - a2 * b1

        return Vector(s1, s2, s3)

        M = Matrix((i3,j3,k3), self.value, other.value)
        return -(M.det)  # don't look at this, it's disgusting but it's kinda cool

    def project(self, basis):
        """
        Return projection of vector in given basis.
        :param basis: iterable of Vectors
        :return: Vector
        """
        res = Vector(0, 0, 0)
        for base in basis:
            res += (self.dot(base)/base.dot(base)) * base
        return res
