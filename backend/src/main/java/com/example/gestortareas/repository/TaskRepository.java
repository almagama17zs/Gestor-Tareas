package com.example.gestortareas.repository;


import com.example.gestortareas.model.Task;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;


import java.util.List;


@Repository
public interface TaskRepository extends JpaRepository<Task, Long> {
List<Task> findByCompleted(boolean completed);
List<Task> findByTitleContainingIgnoreCase(String q);
}