# Laravel: Eloquent ORM

Interacting with your database using Laravel's Object-Relational Mapper (ORM), Eloquent.

## Core Concept

Eloquent provides a simple, ActiveRecord implementation for working with your database. Each database table has a corresponding "Model" class which is used to interact with that table. Models allow you to query for data in your tables, as well as insert, update, and delete records.

## Defining Models (`app/Models/`)

*   **Convention:** Models typically reside in the `app/Models` directory (though older Laravel versions placed them in `app/`).
*   **Artisan Command:** Create a new model using `php artisan make:model ModelName [-m]` (the `-m` flag also creates a corresponding database migration file).
*   **Structure:** Eloquent models extend the `Illuminate\Database\Eloquent\Model` class.
*   **Table Name:** By default, Eloquent assumes the table name is the plural, snake_case version of the model name (e.g., `User` model maps to `users` table). You can override this by setting the `$table` property: `protected $table = 'my_users';`.
*   **Primary Key:** Assumes `id` as the primary key. Override with `protected $primaryKey = 'my_id';`. Set `$incrementing = false` if it's not auto-incrementing. Set `$keyType = 'string'` if it's not an integer.
*   **Timestamps:** Eloquent expects `created_at` and `updated_at` columns by default and manages them automatically. Disable with `public $timestamps = false;`.
*   **Mass Assignment (`$fillable` / `$guarded`):**
    *   To protect against mass-assignment vulnerabilities when using `Model::create()` or `model->update()`, you **must** define either `$fillable` (allow only these attributes) or `$guarded` (block these attributes). `$fillable` is generally recommended.
    *   `protected $fillable = ['name', 'email', 'bio'];`
    *   `protected $guarded = ['id', 'is_admin'];` (Less common, blocks listed fields)

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\BelongsTo; // Corrected import
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Post extends Model
{
    use HasFactory; // Enables model factories for testing/seeding

    /**
     * The table associated with the model.
     *
     * @var string
     */
    // protected $table = 'blog_posts'; // Example: Custom table name

    /**
     * The attributes that are mass assignable.
     *
     * @var array<int, string>
     */
    protected $fillable = [
        'title',
        'slug',
        'content',
        'user_id', // Foreign key
        'is_published',
        'published_at', // Added published_at
    ];

    /**
     * The attributes that should be cast.
     * Cast attributes to common data types.
     *
     * @var array<string, string>
     */
    protected $casts = [
        'is_published' => 'boolean',
        'published_at' => 'datetime',
    ];

    /**
     * Get the user that owns the post.
     */
    public function user(): BelongsTo // Type hint for relationship
    {
        // Assumes a user_id foreign key column exists on the posts table
        return $this->belongsTo(User::class);
    }

    /**
     * The tags that belong to the post.
     */
    public function tags(): BelongsToMany
    {
        // Assumes a 'post_tag' pivot table exists with 'post_id' and 'tag_id'
        return $this->belongsToMany(Tag::class);
        // ->withTimestamps(); // Optionally manage timestamps on pivot table
        // ->withPivot('is_primary'); // Optionally access extra pivot table columns
    }

     /**
     * Get the comments for the blog post.
     */
    public function comments(): HasMany
    {
        // Assumes the Comment model has a 'post_id' foreign key
        return $this->hasMany(Comment::class);
    }
}
```

## Relationships

Define methods on your model class to represent relationships:

*   **One To One:** `hasOne()`, `belongsTo()` (use `unique()` constraint on foreign key).
*   **One To Many:** `hasMany()` (on the "one" side), `belongsTo()` (on the "many" side).
*   **Many To Many:** `belongsToMany()` (on both sides). Requires a pivot table (e.g., `post_tag` table for `Post` and `Tag` models).
*   **Polymorphic:** `morphTo()`, `morphMany()`, `morphToMany()`, `morphedByMany()`. For relationships where a model can belong to more than one other type of model.

## Retrieving Data (Query Builder / Eloquent)

*   **`Model::all()`**: Retrieve all records.
*   **`Model::find($id)`**: Retrieve a model by its primary key. Returns `null` if not found.
*   **`Model::findOrFail($id)`**: Like `find()`, but throws `ModelNotFoundException` if not found.
*   **`Model::where('column', 'operator', 'value')`**: Start building a query.
    *   Operators: `=`, `>`, `<`, `>=`, `<=`, `!=`, `like`, `not like`, `in`, `not in`, `between`, `not between`, `null`, `not null`, etc.
    *   Chain multiple `where()` calls (they act as `AND`). Use `orWhere()` for `OR`.
*   **`->first()`**: Execute the query and get the first result.
*   **`->get()`**: Execute the query and get all results as an Eloquent Collection.
*   **`->count()`**: Get the count of matching records.
*   **`->exists()` / `->doesntExist()`**: Check if any matching records exist.
*   **`->orderBy('column', 'asc|desc')`**: Order results.
*   **`->limit($n)` / `->take($n)`**: Limit the number of results.
*   **`->skip($n)` / `->offset($n)`**: Skip results (for pagination).
*   **`->paginate($perPage)`**: Paginate results easily (returns a Paginator instance).
*   **Eager Loading (Performance):** Prevent N+1 query problems when accessing relationships.
    *   **`with('relationshipName')`**: Load specified relationships along with the main model.
    *   **`Model::with('comments', 'tags')->find($id);`**
    *   **`Model::where(...)->with('user')->get();`**

```php
// Find post with ID 1
$post = Post::find(1);

// Find published posts by a specific user, ordered by date
$posts = Post::where('is_published', true)
             ->where('user_id', $userId)
             ->orderBy('published_at', 'desc')
             ->limit(10)
             ->get();

// Get a post by slug, fail if not found
$post = Post::where('slug', $slug)->firstOrFail();

// Eager load author and tags for multiple posts
$posts = Post::with('user', 'tags')->paginate(15);
foreach ($posts as $post) {
    echo $post->title;
    echo $post->user->name; // No extra query needed
    foreach ($post->tags as $tag) { // No extra query needed
        echo $tag->name;
    }
}
```

## Inserting & Updating Data

*   **Create (Mass Assignment):**
    ```php
    $post = Post::create([
        'title' => $request->input('title'),
        'content' => $request->input('content'),
        'user_id' => auth()->id(), // Assuming user is logged in
        'is_published' => $request->boolean('is_published'),
    ]);
    ```
*   **Create (Instance):**
    ```php
    $post = new Post();
    $post->title = $request->input('title');
    $post->content = $request->input('content');
    $post->user_id = auth()->id();
    $post->save(); // Save the new model instance
    ```
*   **Update (Instance):**
    ```php
    $post = Post::findOrFail($id);
    $post->title = $request->input('title');
    // ... update other fields ...
    $post->save(); // Save the changes
    ```
*   **Update (Mass Assignment):**
    ```php
    $post = Post::findOrFail($id);
    $post->update($request->only(['title', 'content', 'is_published'])); // Only update fillable fields provided
    ```
*   **Update (Query Builder):** Updates directly in the database (bypasses model events/mutators).
    ```php
    Post::where('is_published', false)->update(['status' => 'archived']);
    ```

## Deleting Data

*   **Instance:**
    ```php
    $post = Post::findOrFail($id);
    $post->delete();
    ```
*   **Query Builder:**
    ```php
    Post::where('user_id', $userId)->delete();
    ```
*   **Soft Deletes:** If your model uses the `SoftDeletes` trait, `delete()` sets the `deleted_at` timestamp instead of removing the record. Use `forceDelete()` to permanently remove. Query normally excludes soft-deleted records; use `withTrashed()` or `onlyTrashed()` to include them.

Eloquent provides an expressive and convenient way to interact with your database in Laravel applications.

*(Refer to the official Laravel Eloquent documentation: https://laravel.com/docs/eloquent)*