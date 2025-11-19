package com.example.gestortareas.service;


import com.example.gestortareas.model.Task;
import com.example.gestortareas.repository.TaskRepository;
import org.springframework.stereotype.Service;


import java.time.LocalDateTime;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;


@Service
public class TaskService {
private final TaskRepository repo;


public TaskService(TaskRepository repo) {
this.repo = repo;
}


public Task create(Task t) {
return repo.save(t);
}


public Optional<Task> get(Long id) { return repo.findById(id); }


public List<Task> listAll() { return repo.findAll(); }


public Task update(Long id, Task updated) {
return repo.findById(id).map(t -> {
t.setTitle(updated.getTitle());
t.setDescription(updated.getDescription());
t.setPriority(updated.getPriority());
t.setEstimatedMinutes(updated.getEstimatedMinutes());
t.setDueDate(updated.getDueDate());
t.setCompleted(updated.isCompleted());
return repo.save(t);
}).orElseThrow(() -> new RuntimeException("Task not found"));
}


public void delete(Long id) { repo.deleteById(id); }


public List<Task> search(String q) { return repo.findByTitleContainingIgnoreCase(q); }


public List<Task> getPending() { return repo.findByCompleted(false); }


/**
* Simple intelligent prioritization:
* Score each task by:
* - priority (lower number = more important)
* - due date closeness
* - estimated time (shorter tasks first to get quick wins)
*/
public List<Task> suggestOrder() {
List<Task> pending = getPending();
LocalDateTime now = LocalDateTime.now();
return pending.stream()
.sorted(Comparator.comparingDouble(this::scoreTask))
.collect(Collectors.toList());
}


private double scoreTask(Task t) {
// lower is better
double p = t.getPriority(); // 1..5
double priorityFactor = p; // directly


double dueFactor = 10.0; // default if no due date
if (t.getDueDate() != null) {
long hoursToDue = java.time.Duration.between(LocalDateTime.now(), t.getDueDate()).toHours();
// if overdue, make it very high urgency
if (hoursToDue <= 0) dueFactor = 0.1;
else dueFactor = Math.max(0.1, (double) hoursToDue / 24.0); // days remaining scaled
}


double timeFactor = Math.max(1.0, t.getEstimatedMinutes() / 30.0); // prefer shorter tasks


// Combine: weight prioritizing priority and due date
double score = priorityFactor * 2.0 + dueFactor * 1.5 + timeFactor * 1.0;
return score;
}
}