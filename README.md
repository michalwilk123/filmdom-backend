# filmdom-backend

### Tasks:

- [x] user authorization
- [x] user authentication
- [x] configure django
- [x] rating
- [x] postgres support
- [x] docker (docker composer)
- [x] added celery
- [x] added import data job to fetch data about movies

## Filters:
I am aware of existance of package [django-filter](https://django-filter.readthedocs.io/en/stable/index.html) 
and I am certain it is not nessessary for this perticular use case. 

To implement current logic i would need to create at least 2-4 filter classes
(need to filter by: ordering, fieldnames, search),
modify tests and also modify api calls in the frontend. 
 
More that that some functionalities, (like limiting results and ordering 
by parameters calculated on the fly) would be even harder to implement and maintain.
 
 So for the time being I will be leaving the filter logic class as it is.
