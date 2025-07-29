def multiply_matrices(A, B):
    # Check dimension compatibility
    if len(A[0]) != len(B):
        raise ValueError("Number of columns in A must equal number of rows in B")

    result = []
    for i in range(len(A)):
        row = []
        for j in range(len(B[0])):
            product = 0
            for k in range(len(B)):
                product += A[i][k] * B[k][j]
            row.append(product)
        result.append(row)
    return result
