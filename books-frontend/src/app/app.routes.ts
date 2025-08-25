import { Routes } from '@angular/router';
import { RegisterComponent } from './register/register.component';
import { LoginComponent } from './login/login.component';
import { BooksListComponent } from './books-list/books-list.component';
import { ViewBooksComponent } from './view-books/view-books.component';

export const routes: Routes = [
    { path: 'register', component: RegisterComponent },
    { path: 'login', component: LoginComponent },
    { path: 'books', component: BooksListComponent },
    { path: 'view-books', component: ViewBooksComponent },
    { path: '', redirectTo: '/register', pathMatch: 'full' }
];
