import { MutationKey, UseMutationOptions, useMutation, useMutationState, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

export const useMutationData = <TData = unknown, TVariables = unknown, TContext = unknown>(
  mutationKey: MutationKey,
  mutationFn: (variables: TVariables) => Promise<TData>,
  queryKey?: string | string[],
  onSuccess?: (data: TData) => void,
  options?: Omit<UseMutationOptions<TData, Error, TVariables, TContext>, 'mutationKey' | 'mutationFn' | 'onSuccess'>
) => {
  const queryClient = useQueryClient();

  const mutation = useMutation<TData, Error, TVariables, TContext>({
    mutationKey: [mutationKey],
    mutationFn,
    onSuccess: (data) => {
      if (onSuccess) onSuccess(data);
      return toast.success("Success", {description: "Operation completed successfully"});
    },
    onSettled: async () => {
      if (queryKey) queryClient.invalidateQueries({ queryKey: Array.isArray(queryKey) ? queryKey : [queryKey] });
    },
    ...options
  });

  return mutation;
};

export const useMutationDataState = <TVariables = unknown>(mutationKey: MutationKey) => {
  const data = useMutationState({
    filters: { mutationKey },
    select: (mutation) => {
      return {
        variables: mutation.state.variables as TVariables,
        status: mutation.state.status,
      }
    },
  })
  
  const latestVariables = data[data.length - 1]
  return { latestVariables }
} 