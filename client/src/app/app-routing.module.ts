import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { StepsComponent } from './steps/steps.component';

const routes: Routes = [
  { path: '', component: StepsComponent }, 
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
