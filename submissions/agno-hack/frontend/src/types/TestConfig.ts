export interface ScreenshotInstruction {
  step_description: string;
  filename: string;
}

export interface TestConfig {
  target_url: string;
  task_description: string;
  screenshot_instructions: ScreenshotInstruction[];
  name?: string;
  created_at?: string;
}

export interface SavedWorkflow {
  id: string;
  name: string;
  config: TestConfig;
  created_at: string;
}