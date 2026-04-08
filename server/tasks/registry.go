package tasks

import (
	"rl_env/server/env"
)

// TaskGenerator is a function that returns a pre-configured invoice task.
type TaskGenerator func() *env.Invoice

var registry = make(map[string]TaskGenerator)

// Register adds a new task generator to the global registry.
func Register(name string, gen TaskGenerator) {
	registry[name] = gen
}

// GetTask returns an invoice by its task ID/name.
func GetTask(name string) *env.Invoice {
	if gen, ok := registry[name]; ok {
		return gen()
	}
	return nil
}

// ListTasks returns all registered task names.
func ListTasks() []string {
	tasks := make([]string, 0, len(registry))
	for name := range registry {
		tasks = append(tasks, name)
	}
	return tasks
}
