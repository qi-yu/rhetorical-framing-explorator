import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup } from '@angular/forms';
import { FeatureService } from './feature.service';
import { IFeature } from './feature';

@Component({
  selector: 'app-feature-selection',
  templateUrl: './feature-selection.component.html',
  styleUrls: ['./feature-selection.component.css']
})
export class FeatureSelectionComponent implements OnInit {
  checked: boolean = true;
  selectedFeatures: Array<IFeature> = [];
  allFeatures: Array<IFeature> = [];
  allDimensions: Array<string> = [];
  errorMsg: any;

  constructor(private featureService: FeatureService) {

  }

  onToggleSelectAll() {
    if(this.checked === false) {
      this.featureService.getAllFeatures()
        .subscribe({
          next: data => this.selectedFeatures = data
        })
    } else {
      this.selectedFeatures = [];
    }
  }

  onSelectFeature() {
    this.checked = false;
    this.selectedFeatures.length === 0 ? this.checked  = true : this.checked = false;
  }

  ngOnInit(): void {
    this.featureService.getAllFeatures().subscribe({
      next: data => {
        this.allFeatures = data;
        this.allDimensions = [...new Set(data.map((item) => item.dimension))]
      }
    })
  }
}
