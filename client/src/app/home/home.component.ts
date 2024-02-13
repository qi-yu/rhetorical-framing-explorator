import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.css']
})
export class HomeComponent {
  functionalities = [
    {
      name: 'Rhetorical Framing Explorator', 
      route: '/rhetorical-framing'
    }, 
    {
      name: 'Keyword Explorator',
      route: '/keyword'
    }
  ];

  responsiveOptions: any[] = [];

  constructor(private router: Router) {}

  startFunctionality(functionality: any) {
    this.router.navigate([functionality.route]);
  }

  ngOnInit() {
      this.responsiveOptions = [
          {
              breakpoint: '1199px',
              numVisible: 1,
              numScroll: 1
          },
          {
              breakpoint: '991px',
              numVisible: 2,
              numScroll: 1
          },
          {
              breakpoint: '767px',
              numVisible: 1,
              numScroll: 1
          }
      ];
  }
}
