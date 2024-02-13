import { Component, EventEmitter, Input, Output } from '@angular/core'; 

@Component({
  selector: 'app-keyword-explorator',
  templateUrl: './keyword-explorator.component.html',
  styleUrls: ['./keyword-explorator.component.css']
})
export class KeywordExploratorComponent {
  selectedMethod: any = null;

  methods: any[] = [
      { name: 'Pointwise Mutual Information', key: 'pmi' },
      { name: 'Pointwise Mutual Information (mitigated by word frequency)', key: 'pmi-freq' },
  ];

  ngOnInit() {
      this.selectedMethod = this.methods[0];
  }
}
