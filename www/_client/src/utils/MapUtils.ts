export const countUnique = (data: string[]):Map<string, number> => {
    const unique = [...new Set(data)];
    const stats = new Map(unique.map(i => [i, 0]));

    data.forEach(i => stats.set(i, stats.get(i)! + 1));

    return new Map(
        [...stats.entries()]
            .sort((a, b) => b[1] - a[1])
    );
}