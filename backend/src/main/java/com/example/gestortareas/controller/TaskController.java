package com.example.gestortareas.controller;


import com.example.gestortareas.model.Task;
import com.example.gestortareas.service.TaskService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;


import java.net.URI;
import java.util.List;


@RestController
@RequestMapping("/api/tasks")
@CrossOrigin(origins = "*")
public class TaskController {
private final TaskService service;


public TaskController(TaskService service) {
this.service = service;
}


@GetMapping
public List<Task> list() { return service.listAll(); }


@GetMapping("/pending")
public List<Task> pending() { return service.getPending(); }


@GetMapping("/suggest")
public List<Task> suggest() { return service.suggestOrder(); }


@GetMapping("/{id}")
public ResponseEntity<Task> get(@PathVariable Long id) {
return service.get(id)
.map(ResponseEntity::ok)
.orElse(ResponseEntity.notFound().build());
}


@PostMapping
public ResponseEntity<Task> create(@RequestBody Task t) {
Task created = service.create(t);
return ResponseEntity.created(URI.create("/api/tasks/" + created.getId())).body(created);
}


@PutMapping("/{id}")
public ResponseEntity<Task> update(@PathVariable Long id, @RequestBody Task t) {
try {
Task updated = service.update(id, t);
return ResponseEntity.ok(updated);
} catch (RuntimeException ex) {
return ResponseEntity.notFound().build();
}
}


@DeleteMapping("/{id}")
public ResponseEntity<Void> delete(@PathVariable Long id) {
service.delete(id);
return ResponseEntity.noContent().build();
}


@GetMapping("/search")
public List<Task> search(@RequestParam String q) { return service.search(q); }
}