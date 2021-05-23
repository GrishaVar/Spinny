from math import sqrt
from operator import mul, add


class VectorSpace:
    _IS_MATRIX = False
    _IS_VECTOR = False

    def __add__(self, other):
        raise NotImplementedError("Addition not implemented")

    def __radd__(self, other):
        # Vector Space addition is commutative
        return self + other

    def __mul__(self, other):
        raise NotImplementedError('Scaling not implemented')

    def __rmul__(self, other):
        # Vector Space scaling is commutative
        return self * other

    def __neg__(self):
        return self * -1

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return other + -self

    def __eq__(self, other):
        raise NotImplementedError('Equality not implemented')

    def __abs__(self):
        raise NotImplementedError('Norm not implemented')


class Matrix(VectorSpace):  # TODO extract matrix and common to linalg module?
    """
    Matrix implementation. Index with M[i,j] (start at zero!)

    Supports addition (+), subtraction (-),
    negation (-m), scaling (*),
    matrix multiplication(@), powers (**).

    det(self) returns determinant (memoised).
    transpose(m) returns m transposed.
    row_switch(self, i, j) elementary row operation swap.
    row_mult(self, i, m) elementary row operation multiply.
    row_add(self, i, j, m) elementary row operation add.

    size: (#rows, #cols)
    is_square: #rows == #cols
    """
    _IS_MATRIX = True

    def __init__(self, rows, det=None):  # assumes input is tuple of tuples!
        self._value = rows
        m = len(rows)
        n = len(rows[0])
        self.size = (m, n)
        self.is_square = m == n
        self._det = det

    @property
    def det(self):
        """
        Calculate and store determinant.
        :return: int
        """
        if self._det is None:  # kinda-sorta-memoised determinant
            v = self._value
            m, n = self.size
            if not self.is_square:
                self._det = 0
            elif m == 1:
                self._det = v[0][0]
            elif m == 2:
                self._det = (
                    v[0][0]*v[1][1] -
                    v[0][1]*v[1][0]
                )
            elif m == 3:
                # a(ei - fh) - b(di - fg) + c(dh - eg)
                self._det = (
                    v[0][0]*(v[1][1]*v[2][2] - v[1][2]*v[2][1]) -
                    v[0][1]*(v[1][0]*v[2][2] - v[1][2]*v[2][0]) + 
                    v[0][2]*(v[1][0]*v[2][1] - v[1][1]*v[2][0])
                )  # I would feel bad about doing this if it wasn't the best way
            else:
                raise NotImplementedError('High order det not implemented yet')
        return self._det

    def __repr__(self):
        res_parts = []
        for row in self._value:
            res_parts.append('\t'.join(map(str, row)))
        res = ')\n('.join(res_parts)
        return '(' + res + ')'

    def __getitem__(self, pos):
        """index row with M[int] or value with M[int,int]. Index from 0."""
        try:
            i, j = pos
            return self._value[i][j]
        except TypeError:  # pos not a tuple => requesting full row
            return self._value[pos]

    def __setitem__(self, pos, x):
        """index row with M[int] or value with M[int,int]. Index from 0."""
        try:
            i, j = pos
            self._value[i][j] = x
        except TypeError:  # pos not a tuple => requesting full row
            self._value[pos] = x

    def __add__(self, other):
        if other is 0:
            # for sum()
            # this causes a warning but
            # I thought about it and "is 0" is what I want
            return self
        #size = self.size
        #if size != other.size:
        #    raise ValueError('Different Sizes!')
        m, n = self.size
        a = self._value
        b = other._value
        c = tuple(
            tuple(
                a[i][j] + b[i][j] for j in range(n)
            ) for i in range(m)
        )
        return Matrix(c)

    def __mul__(self, a):
        """Scalar multiplication."""
        m, n = self.size
        b = self._value
        c = tuple(
            tuple(
                a * b[i][j] for j in range(n)
            ) for i in range(m)
        )

        if (det := self._det) is not None:
            det *= a
        return Matrix(c, det)

    def __matmul__(self, other):
        if not other._IS_MATRIX:
            return NotImplemented

        if self.size[1] != other.size[0]:
            raise ValueError('Incompatible Sizes')
        # TODO make some toggleable thing to supress all checks

        a = self._value
        b = other._value
        c = tuple(
            tuple(
                sum(map(mul, a_row, b_col))
                for b_col in zip(*b)
            ) for a_row in a
        )  # I'm quite pleased with myself

        if (det := self._det) is not None and (b_det := other._det) is not None:
            det *= b_det

        return Matrix(c, det)

    def __pow__(self, other):
        # TODO: update to matmul (preferably without creating n Matrix objs)
        raise NotImplementedError('see todo')
        res = self
        for x in range(other-1):
            res *= self
        return res

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        if (res := self._hash) is None:
            res = self._hash = hash(self._value)
        return res

    def transpose(self):
        return Matrix(tuple(zip(*self._value)))

    def to_vector(self):
        """
        Converts single-column or single-row matrix into a vector.
        :return: Vector
        """
        m, n = self.size
        if m == 1:
            return Vector(self._value[0])
        if n == 1:
            return Vector(tuple(zip(*self._value))[0])
        raise ValueError('Incompatible size')

    def copy(self):
        # immutable, so this should be fine I think?
        return self

    def row_switch(self, i, j):
        """
        NOT UPDATED FOR IMMUTABLE MATRICES
        Swap row positions.
        :param i: index of row 1
        :param j: index of row 2
        """
        raise NotImplementedError('see todo')
        self._value[i], self._value[j] = self._value[j], self._value[i]

    def row_mult(self, i, m):
        """
        NOT UPDATED FOR IMMUTABLE MATRICES
        Multiply a row by a scalar.
        :param i: index of row
        :param m: non-zero scalar
        """
        raise NotImplementedError('see todo')
        if m == 0:
            raise ValueError("m can't be zero!")
        self._value[i] = [m*x for x in self._value[i]]

    def row_add(self, i, j, m):
        """
        NOT UPDATED FOR IMMUTABLE MATRICES
        Add a row to another (with scaling).
        :param i: index of row to be changed
        :param j: index of row to add
        :param m: non-zero scalar
        :return:
        """
        raise NotImplementedError('see todo')
        if m == 0:
            raise ValueError("m can't be zero!")
        self._value[i] = [x+m*y for x, y in zip(self._value[i], self._value[j])]


class Vector(VectorSpace):
    """
    Vector implementation. Index with V[i] (start at zero)
    Treated as vertical.

    Does NOT support vector*matrix multiplication
    (convert the vector to a matrix and do m*m)

    vector@vector returns dot product

    length_squared() returns the square of abs (memoised)
    length and __abs__() returns euclidean norm (memoised).
    norm(n) returns n-th norm
    cross(other) return cross product.
    project(basis) return projection onto basis.

    size: #entries
    """

    _IS_VECTOR = True

    def __init__(self, values):
        self._value = values
        self.size = len(values)
        #if self.n == 0:
        #    raise ValueError('Vector of size zero')
        self._length = None

    def __repr__(self):
        return '(' + (', '.join(str(x) for x in self._value)) + ')ᵗ'
        # add rounding
        # add horizontal vectors (?)
        # change to fstring

    def __getitem__(self, pos):
        return self._value[pos]

    def __add__(self, other):
        if other is 0:
            # for sum()
            # this causes a warning but
            # I thought about it and "is 0" is what I want
            return self

        a = self._value
        b = other._value
        return Vector(tuple(map(add, a, b)))

    def __mul__(self, a):  # scalar multiplication only!
        return Vector(tuple(a*b for b in self._value))

    def __matmul__(self, other):  # v@v
        a = self._value
        b = other._value
        return sum(map(mul, a, b))

    def __rmatmul__(self, other):  # m@v multiplication
        a = other._value
        b = self._value
        c = tuple(sum(map(mul, a_row, b)) for a_row in a)
        return Vector(c)

    def __hash__(self):
        return hash(self._value)

    def __eq__(self, other):
        return hash(self) == hash(other)

    @property
    def length_squared(self):
        return self@self

    @property
    def length(self):  # another semi-memoised expensive function
        """
        Returns euclidean norm of vector.
        :return: int
        """
        if self._length is None:
            self._length = sqrt(self.length_squared)
        return self._length

    @property
    def unit(self):
        return (1/self.length) * self

    def to_matrix(self, vert=True):
        """Converts Vector to Matrix."""
        if vert:
            return Matrix(tuple(zip(self._value)))
        return Matrix((self._value,))

    def copy(self):
        return self

    def orthant(self):
        res = 0
        for n in self._value:
            res *= 2
            if n > 0:
                res += 1
        return res

    def cross(self, other):
        """
        Cross Product. Only defined for 3 dimensional vectors.
        :param other: Vector
        :return: self⨯other
        """
        # Also exists for 7 dimensions... implement?

        a1, a2, a3 = self._value
        b1, b2, b3 = other._value

        s1 = a2 * b3 - a3 * b2
        s2 = a3 * b1 - a1 * b3
        s3 = a1 * b2 - a2 * b1

        return Vector((s1, s2, s3))

    def project(self, basis):
        """
        Return projection of vector in given basis.
        :param basis: iterable of Vectors
        :return: Vector
        """
        res = Vector([0, 0, 0])
        for base in basis:
            res += (self@base) / (base@base) * base  # inefficient TODO
        return res

    def crop(self, bound):
        """
        Shorten vector if it's longer than the given bound
        """
        if self.length_squared < bound**2:
            return self
        return bound * self.unit


