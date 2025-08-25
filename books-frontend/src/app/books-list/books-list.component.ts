import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-books-list',
  standalone: true,
  templateUrl: './books-list.component.html',
  styleUrl: './books-list.component.css',
  imports: [CommonModule,FormsModule]
})
export class BooksListComponent {
  books: any[] = [];
  role: string | null = localStorage.getItem('role');
  token: string | null = localStorage.getItem('token');
  message = '';
  // For add/edit forms
  newBook = { title: '', author: '' };
  editingBookId: number | null = null;
  editBookData = { title: '', author: '' };

  constructor(private http: HttpClient) {
    this.fetchBooks();
  }

  fetchBooks() {
    const token = localStorage.getItem('token');
    this.http.get<any[]>('http://localhost:5000/books', {
      headers: { Authorization: `Bearer ${token}` }
    }).subscribe({
      next: (res: any) => this.books = res,
      error: (err) => this.message = err.error.error || 'Error fetching books'
    });
  }

  deleteBook(bookId: number) {
    if (this.role !== 'admin' && this.role !== 'author') {
      this.message = 'Only admins and authors can delete books.';
      return;
    }
    this.http.delete(`http://localhost:5000/books/${bookId}`, {
      headers: { Authorization: `Bearer ${this.token}` }
    }).subscribe({
      next: (res: any) => {
        this.message = res.message;
        this.fetchBooks(); // Refresh list
      },
      error: (err) => this.message = err.error.error || 'Error deleting book'
    });
  }

  startEditBook(book: any) {
    if (this.role !== 'author' && this.role !== 'admin') {
      this.message = 'Only authors and admins can edit books.';
      return;
    }
    this.editingBookId = book.id;
    this.editBookData = { title: book.title, author: book.author };
  }

  submitEditBook(bookId: number) {
    if (!this.editBookData.title || !this.editBookData.author) {
      this.message = 'Title and author are required.';
      return;
    }
    this.http.put(`http://localhost:5000/books/${bookId}`, {
      title: this.editBookData.title,
      author: this.editBookData.author
    }, {
      headers: { Authorization: `Bearer ${this.token}` }
    }).subscribe({
      next: (res: any) => {
        this.message = 'Book updated successfully.';
        this.fetchBooks();
        this.editingBookId = null;
      },
      error: (err) => this.message = err.error.error || 'Error updating book'
    });
  }

  cancelEditBook() {
    this.editingBookId = null;
  }

  submitAddBook() {
    if (this.role !== 'author' && this.role !== 'admin') {
      this.message = 'Only authors and admins can add books.';
      return;
    }
    if (!this.newBook.title || !this.newBook.author) {
      this.message = 'Title and author are required.';
      return;
    }
    this.http.post('http://localhost:5000/books', {
      title: this.newBook.title,
      author: this.newBook.author
    }, {
      headers: { Authorization: `Bearer ${this.token}` }
    }).subscribe({
      next: (res: any) => {
        this.message = 'Book added successfully.';
        this.fetchBooks();
        this.newBook = { title: '', author: '' };
      },
      error: (err) => this.message = err.error.error || 'Error adding book'
    });
  }
}
