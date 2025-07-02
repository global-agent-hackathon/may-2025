import { QueryKey, UseQueryOptions, useQuery } from "@tanstack/react-query"

export const useQueryData = <TData = unknown>(
    queryKey: QueryKey,
    queryFn: () => Promise<TData>,
    options?: Omit<UseQueryOptions<TData, Error, TData>, 'queryKey' | 'queryFn'>
) => {
    const {data, isPending, isFetched, refetch, isFetching} = useQuery<TData, Error, TData>({
        queryKey,
        queryFn,
        ...options
    })

    return {data, isPending, isFetched, refetch, isFetching}
} 