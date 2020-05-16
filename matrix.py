from math import sqrt


class VectorSpace:
    def __add__(self, other):
        raise NotImplementedError("Addition not implemented")

    def __radd__(self, other):  # Vector Space addition is commutative
        return self + other

    def __mul__(self, other):
        raise NotImplementedError('Scaling not implemented')

    def __rmul__(self, other):  # Vector Space scaling is commutative
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


class Matrix(VectorSpace):
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

    _value: list of values.
    n: number of rows.
    m: number of columns.
    """
    _IS_MATRIX = True
    _IS_VECTOR = False

    def __init__(self, rows):  # assumes input is list of lists!
        self._value = rows
        self.n = len(rows)
        # if self.n == 0:
        #     raise ValueError('Matrix with zero rows')
        self.m = len(rows[0])
        # if self.m == 0:
        #     raise ValueError('Matrix with zero columns')
        # for i, row in enumerate(self._value):
        #     if len(row) != self.m:
        #         raise ValueError('Matrix with unequal row lengths')
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
            v = self._value
            if self.n != self.m:
                self._det = 0
            elif self.n == 1:
                self._det = v[0][0]
            elif self.n == 2:
                self._det = (
                    v[0][0]*v[1][1] -
                    v[0][1]*v[1][0]
                )
            elif self.n == 3:
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
        if other == 0:  # allows sum()
            return self
        # if not isinstance(other, Matrix):
        #    raise TypeError('Incompatible type: {}'.format(type(other)))
        if self.size != other.size:
            raise ValueError('Different Sizes')

        res = []
        res_append = res.append  # avoid dots in expensive loops
        self_value = self._value
        other_value = other._value  # other._value is private you need at add a other.getvalue()
        n, m = self.size
        for i in range(n):
            row = []
            row_append = row.append
            for j in range(m):
                row_append(self_value[i][j] + other_value[i][j])
            res_append(row)
        return Matrix(res)

    def __mul__(self, other):
        """Scalar multiplication."""  # TODO implement elementwise M*M?
        self_value = self._value  # avoid dots in expensive loops
        self_n, self_m = self.size
        res = []
        res_append = res.append

        for i in range(self_n):
            row = []
            row_append = row.append
            for j in range(self_m):
                row_append(other * self_value[i][j])
            res_append(row)
        return Matrix(res)

    def __matmul__(self, other):
        self_value = self._value  # avoid dots in expensive loops
        self_n, self_m = self.size
        res = []
        res_append = res.append
        v2 = other._value  # other._value is private you need at add a other.getvalue()
        other_n, other_m = other.size
        other_value = other._value  # other._value is private you need at add a other.getvalue()
        if self_m != other_n:
            raise ValueError('Incompatible Sizes')
        if other._IS_VECTOR:  # other is vector => return vector  again other._IS_VECTOR is private
        # if isinstance(other, Vector):
            for i in range(self_n):
                value = 0
                for j in range(self_m):
                    value += self_value[i][j] * other_value[j]
                res_append(value)
            return Vector(res)
        else:  # other is matrix => return matrix
            for i in range(self_n):
                row = []
                row_append = row.append
                for j in range(other_m):
                    value = 0
                    for k in range(self_m):
                        value += self_value[i][k] * other_value[k][j]
                    row_append(value)
                res_append(row)
            res = Matrix(res)
            if None not in (self._det, other._det):
                res._det = self._det * other._det  # might as well
            return res

    def __pow__(self, other):
        res = self
        for x in range(other-1):
            res *= self
        return res

    def __eq__(self, other):
        return isinstance(other, Matrix) and self._value == other._value

    @staticmethod
    def transpose(m):
        return Matrix(list(zip(*m._value)))  # bro?

    def to_vector(self):
        """
        Converts single-column matrix into a vector.
        :return: Vector
        """
        if self.m != 1:
            return ValueError('Not a vector')
        return Vector(list(zip(*self._value)))
        # could be done with transpose but it makes matrix which takes too long
        # TODO is this a list of lists?

    def copy(self):
        return Matrix(self._value)

    def row_switch(self, i, j):
        """
        Swap row positions.
        :param i: index of row 1
        :param j: index of row 2
        """
        #value = list(self._value)
        #temp = value[j]
        #value[j] = value[i]
        #value[i] = temp
        #self._value = list(value)
        self._value[i], self._value[j] = self._value[j], self._value[i]

    def row_mult(self, i, m):
        """
        Multiply a row by a scalar.
        :param i: index of row
        :param m: non-zero scalar
        """
        if m == 0:
            raise ValueError("m can't be zero!")
        #value = list(self._value)
        #value[i] = tuple(m*x for x in value[i])
        #self._value = tuple(value)
        self._value[i] = [m*x for x in self._value[i]]

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
        #value = list(self._value)
        #row = tuple(m*x for x in value[j])
        #value[i] = tuple(x+y for x,y in zip(value[i], row))
        #self._value = tuple(value)
        self._value[i] = [x+m*y for x,y in zip(self._value[i], self._value[j])]


class Vector(Matrix):  # these are saved as horizontal but treated as vertical.
    """
    Subclass of Matrix for single-column matrices. Index with M[i,j] (start at zero!)

    length(self) returns euclidean norm (memoised).
    dot(self, other) returns dot product.
    cross(self, other) return cross product.
    project(self, basis) return projection onto basis.

    _value: list of values.
    n: int, number of entries.
    m: int, 1.
    """

    _IS_VECTOR = True

    def __init__(self, values):
        self._value = values
        self.n = len(self._value)
        if self.n == 0:
            raise ValueError('Vector of size zero')
        self.m = 1
        self._length = None

    def __repr__(self):
        return '(' + (', '.join(str(x) for x in self._value)) + ')ᵗ'  # add rounding

    def __getitem__(self, pos):
        return self._value[pos]

    def __setitem__(self, pos, x):
        self._value[pos] = x

    def __add__(self, other):
        if other == 0:  # allows sum()
            return self
        #if not isinstance(other, Vector):
        #    raise TypeError('Incompatible type: {}'.format(type(other)))
        #if self.size != other.size:
        #    raise ValueError('Different Sizes')
        return Vector(list(map(sum, zip(self._value, other._value))))

    def __mul__(self, other):  # scalar multiplication only!
        return Vector([other*a for a in self._value])

    def __matmul__(self, other):  # v@m = m, m@v = v, v@v = int
        if other._IS_VECTOR:
            return self.dot(other)  # v dot w = v^t matmul w
        else:  # doesn't account for v matmul w with len(v)=len(w)=1 TODO
            return self._to_matrix() @ other

    @property
    def length(self):  # another semi-memoised expensive function
        """
        Returns euclidean norm of vector.
        :return: int
        """
        if self._length is None:
            self._length = sqrt(sum([c**2 for c in self._value]))
        return self._length

    def to_matrix(self):
        """Converts Vector to Matrix."""
        return Matrix(list(zip(self._value)))
        # TODO is this a list of lists?

    def copy(self):
        return Vector(self._value)

    def dot(self, other):
        """
        Dot Product.
        :param other: Vector
        :return: self·other
        """
        #if not isinstance(other, Vector):
        #    raise TypeError('Incompatible type: {}'.format(type(other)))
        try:
            #turned = Matrix.transpose(self.to_matrix())
            turned = Matrix([self._value])
            return (turned@other)._value[0]  # matrix only has one element
        except AttributeError:
            raise TypeError('Incompatible type: {}'.format(type(other)))

    def cross(self, other):
        """
        Cross Product. Only defined for 3 dimensional vectors.
        :param other: Vector
        :return: self⨯other
        """
        if not isinstance(other, Vector):
            raise TypeError('Incompatible type: {}'.format(type(other)))
        if not (self.n == other.n == 3):  # Also exists for 7 dimensions... implement?
            raise ValueError('Incompatible Sizes')

        a1, a2, a3 = self._value
        b1, b2, b3 = other._value

        s1 = a2 * b3 - a3 * b2
        s2 = a3 * b1 - a1 * b3
        s3 = a1 * b2 - a2 * b1

        return Vector([s1, s2, s3])

        M = Matrix([[i3,j3,k3], self._value, other._value])
        return -(M.det)  # don't look at this, it's disgusting but it's kinda cool

    def project(self, basis):
        """
        Return projection of vector in given basis.
        :param basis: iterable of Vectors
        :return: Vector
        """
        res = Vector([0, 0, 0])
        for base in basis:
            res += (self.dot(base)/base.dot(base)) * base  # inefficient TODO
        return res

