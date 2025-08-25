import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './register.component.html',
  styleUrl: './register.component.css'
})
export class RegisterComponent {
  username = '';
  email = '';
  password = '';
  account_type = 'viewer';
  message = '';

  constructor(private http: HttpClient, private router: Router) {}

  register() {
    this.http.post('http://localhost:5000/register', {
      username: this.username,
      email: this.email,
      password: this.password,
      account_type: this.account_type
    }).subscribe({
      next: (res: any) => {
        this.message = res.message;
        // Redirect to login page after successful registration
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.message = err.error.error;
      }
    });
  }
}
