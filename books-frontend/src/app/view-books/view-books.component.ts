import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-view-books',
  standalone: true,
  templateUrl: './view-books.component.html',
  styleUrl: './view-books.component.css',
  imports: [CommonModule, FormsModule, RouterModule]
})
export class ViewBooksComponent {
  books: any[] = [];
  myBooks: any[] = [];
  searchTerm = '';
  role: string | null = localStorage.getItem('role');
  token: string | null = localStorage.getItem('token');
  message = '';

  constructor(private http: HttpClient) {
    this.fetchAllBooks();
    if (this.role === 'author') {
      this.fetchMyBooks();
    }
  }

  fetchAllBooks() {
    this.http.get<any[]>('http://localhost:5000/books', {
      headers: { Authorization: `Bearer ${this.token}` }
    }).subscribe({
      next: (res: any) => this.books = res,
      error: (err) => this.message = err.error.error || 'Error fetching books'
    });
  }

  fetchMyBooks() {
    this.http.get<any[]>('http://localhost:5000/mybooks', {
      headers: { Authorization: `Bearer ${this.token}` }
    }).subscribe({
      next: (res: any) => this.myBooks = res,
      error: (err) => this.message = err.error.error || 'Error fetching my books'
    });
  }

  searchBooks() {
    if (!this.searchTerm.trim()) {
      this.message = 'Enter a search term.';
      return;
    }
    this.http.get<any[]>(`http://localhost:5000/search?query=${encodeURIComponent(this.searchTerm)}`, {
      headers: { Authorization: `Bearer ${this.token}` }
    }).subscribe({
      next: (res: any) => this.books = res,
      error: (err) => this.message = err.error.error || 'Error searching books'
    });
  }
}
