package com.example.gestortareas.model;


import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;


@Entity
@Table(name = "tasks")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Task {
@Id
@GeneratedValue(strategy = GenerationType.IDENTITY)
private Long id;


private String title;


@Column(length = 2000)
private String description;


// Priority: 1 (highest) - 5 (lowest)
private int priority;


// Estimated duration in minutes
private int estimatedMinutes;


private boolean completed;


private LocalDateTime dueDate;


private LocalDateTime createdAt;


private LocalDateTime updatedAt;


@PrePersist
public void prePersist() {
createdAt = LocalDateTime.now();
updatedAt = createdAt;
}


@PreUpdate
public void preUpdate() {
updatedAt = LocalDateTime.now();
}
}