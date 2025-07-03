export const availableActions = [
  {
    name: 'click',
    description: 'Clicks on an element',
    args: [
      {
        name: 'elementId',
        type: 'number',
      },
    ],
  },
  {
    name: 'setValue',
    description: 'Focuses on and sets the value of an input element',
    args: [
      {
        name: 'elementId',
        type: 'number',
      },
      {
        name: 'value',
        type: 'string',
      },
    ],
  },
  {
    name: 'navigate',
    description: 'Navigates to a specified URL',
    args: [
      {
        name: 'url',
        type: 'string',
      },
    ],
  },
  {
    name: 'waiting',
    description: 'Waits for a specified number of seconds before continuing to the next action. Useful for waiting for page loads, animations, or dynamic content to appear.',
    args: [
      {
        name: 'seconds',
        type: 'number',
      },
    ],
  },
  {
    name: 'finish',
    description: 'Indicates the task is finished',
    args: [],
  },
  {
    name: 'fail',
    description: 'Indicates that you are unable to complete the task',
    args: [
      {
        name: 'message',
        type: 'string',
      },
    ],
  },
  {
    name: 'respond',
    description: 'Provides page summaries, text responses, or asks questions to the user, this action will mean the task will end and you can continue with the next step',
    args: [
      {
        name: 'message',
        type: 'string',
      },
    ],
  },
  {
    name: 'memory',
    description: 'Stores information, drafts, or notes for later use without stopping the interaction loop. Useful for drafting content, saving research findings, or storing intermediate results to reference in subsequent steps',
    args: [
      {
        name: 'message',
        type: 'string',
      },
    ],
  },
] as const;

type AvailableAction = (typeof availableActions)[number];

type ArgsToObject<T extends ReadonlyArray<{ name: string; type: string }>> = {
  [K in T[number]['name']]: Extract<
    T[number],
    { name: K }
  >['type'] extends 'number'
    ? number
    : string;
};

export type ActionShape<
  T extends {
    name: string;
    args: ReadonlyArray<{ name: string; type: string }>;
  }
> = {
  name: T['name'];
  args: ArgsToObject<T['args']>;
};

export type ActionPayload = {
  [K in AvailableAction['name']]: ActionShape<
    Extract<AvailableAction, { name: K }>
  >;
}[AvailableAction['name']];