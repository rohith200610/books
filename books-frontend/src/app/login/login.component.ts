import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrl: './login.component.css',
  imports: [FormsModule]
})
export class LoginComponent {
  username = '';
  password = '';
  message = '';

  constructor(private http: HttpClient, private router: Router) {}

  login() {
    this.http.post('http://localhost:5000/login', {
      username: this.username,
      password: this.password
    }).subscribe({
      next: (res: any) => {
        this.message = res.message;
        // Save token and role
        localStorage.setItem('token', res.token);
        localStorage.setItem('role', res.user.account_type);
        // Redirect to books-list page
        this.router.navigate(['/books']);
      },
      error: (err) => this.message = err.error.error
    });
  }
}
