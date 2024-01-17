import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FeatureSelectionComponent } from './feature-selection.component';

describe('FeatureSelectionComponent', () => {
  let component: FeatureSelectionComponent;
  let fixture: ComponentFixture<FeatureSelectionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ FeatureSelectionComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FeatureSelectionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
