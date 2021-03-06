/*
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
 */

#include "BLI_map.hh"

#include "BKE_attribute.h"
#include "BKE_attribute_access.hh"
#include "BKE_geometry_set.hh"
#include "BKE_lib_id.h"
#include "BKE_mesh.h"
#include "BKE_mesh_wrapper.h"
#include "BKE_modifier.h"
#include "BKE_pointcloud.h"
#include "BKE_volume.h"

#include "DNA_collection_types.h"
#include "DNA_object_types.h"

#include "BLI_rand.hh"

#include "MEM_guardedalloc.h"

using blender::float3;
using blender::float4x4;
using blender::Map;
using blender::MutableSpan;
using blender::Span;
using blender::StringRef;
using blender::Vector;

/* -------------------------------------------------------------------- */
/** \name Geometry Component
 * \{ */

GeometryComponent::GeometryComponent(GeometryComponentType type) : type_(type)
{
}

GeometryComponent ::~GeometryComponent()
{
}

GeometryComponent *GeometryComponent::create(GeometryComponentType component_type)
{
  switch (component_type) {
    case GeometryComponentType::Mesh:
      return new MeshComponent();
    case GeometryComponentType::PointCloud:
      return new PointCloudComponent();
    case GeometryComponentType::Instances:
      return new InstancesComponent();
    case GeometryComponentType::Volume:
      return new VolumeComponent();
  }
  BLI_assert(false);
  return nullptr;
}

void GeometryComponent::user_add() const
{
  users_.fetch_add(1);
}

void GeometryComponent::user_remove() const
{
  const int new_users = users_.fetch_sub(1) - 1;
  if (new_users == 0) {
    delete this;
  }
}

bool GeometryComponent::is_mutable() const
{
  /* If the item is shared, it is read-only. */
  /* The user count can be 0, when this is called from the destructor. */
  return users_ <= 1;
}

GeometryComponentType GeometryComponent::type() const
{
  return type_;
}

bool GeometryComponent::is_empty() const
{
  return false;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Geometry Set
 * \{ */

/* This method can only be used when the geometry set is mutable. It returns a mutable geometry
 * component of the given type.
 */
GeometryComponent &GeometrySet::get_component_for_write(GeometryComponentType component_type)
{
  return components_.add_or_modify(
      component_type,
      [&](GeometryComponentPtr *value_ptr) -> GeometryComponent & {
        /* If the component did not exist before, create a new one. */
        new (value_ptr) GeometryComponentPtr(GeometryComponent::create(component_type));
        return **value_ptr;
      },
      [&](GeometryComponentPtr *value_ptr) -> GeometryComponent & {
        GeometryComponentPtr &value = *value_ptr;
        if (value->is_mutable()) {
          /* If the referenced component is already mutable, return it directly. */
          return *value;
        }
        /* If the referenced component is shared, make a copy. The copy is not shared and is
         * therefore mutable. */
        GeometryComponent *copied_component = value->copy();
        value = GeometryComponentPtr{copied_component};
        return *copied_component;
      });
}

/* Get the component of the given type. Might return null if the component does not exist yet. */
const GeometryComponent *GeometrySet::get_component_for_read(
    GeometryComponentType component_type) const
{
  const GeometryComponentPtr *component = components_.lookup_ptr(component_type);
  if (component != nullptr) {
    return component->get();
  }
  return nullptr;
}

bool GeometrySet::has(const GeometryComponentType component_type) const
{
  return components_.contains(component_type);
}

void GeometrySet::remove(const GeometryComponentType component_type)
{
  components_.remove(component_type);
}

void GeometrySet::add(const GeometryComponent &component)
{
  BLI_assert(!components_.contains(component.type()));
  component.user_add();
  GeometryComponentPtr component_ptr{const_cast<GeometryComponent *>(&component)};
  components_.add_new(component.type(), std::move(component_ptr));
}

void GeometrySet::compute_boundbox_without_instances(float3 *r_min, float3 *r_max) const
{
  const PointCloud *pointcloud = this->get_pointcloud_for_read();
  if (pointcloud != nullptr) {
    BKE_pointcloud_minmax(pointcloud, *r_min, *r_max);
  }
  const Mesh *mesh = this->get_mesh_for_read();
  if (mesh != nullptr) {
    BKE_mesh_wrapper_minmax(mesh, *r_min, *r_max);
  }
}

std::ostream &operator<<(std::ostream &stream, const GeometrySet &geometry_set)
{
  stream << "<GeometrySet at " << &geometry_set << ", " << geometry_set.components_.size()
         << " components>";
  return stream;
}

/* This generally should not be used. It is necessary currently, so that GeometrySet can by used by
 * the CPPType system. */
bool operator==(const GeometrySet &UNUSED(a), const GeometrySet &UNUSED(b))
{
  return false;
}

/* This generally should not be used. It is necessary currently, so that GeometrySet can by used by
 * the CPPType system. */
uint64_t GeometrySet::hash() const
{
  return reinterpret_cast<uint64_t>(this);
}

/* Returns a read-only mesh or null. */
const Mesh *GeometrySet::get_mesh_for_read() const
{
  const MeshComponent *component = this->get_component_for_read<MeshComponent>();
  return (component == nullptr) ? nullptr : component->get_for_read();
}

/* Returns true when the geometry set has a mesh component that has a mesh. */
bool GeometrySet::has_mesh() const
{
  const MeshComponent *component = this->get_component_for_read<MeshComponent>();
  return component != nullptr && component->has_mesh();
}

/* Returns a read-only point cloud of null. */
const PointCloud *GeometrySet::get_pointcloud_for_read() const
{
  const PointCloudComponent *component = this->get_component_for_read<PointCloudComponent>();
  return (component == nullptr) ? nullptr : component->get_for_read();
}

/* Returns a read-only volume or null. */
const Volume *GeometrySet::get_volume_for_read() const
{
  const VolumeComponent *component = this->get_component_for_read<VolumeComponent>();
  return (component == nullptr) ? nullptr : component->get_for_read();
}

/* Returns true when the geometry set has a point cloud component that has a point cloud. */
bool GeometrySet::has_pointcloud() const
{
  const PointCloudComponent *component = this->get_component_for_read<PointCloudComponent>();
  return component != nullptr && component->has_pointcloud();
}

/* Returns true when the geometry set has an instances component that has at least one instance. */
bool GeometrySet::has_instances() const
{
  const InstancesComponent *component = this->get_component_for_read<InstancesComponent>();
  return component != nullptr && component->instances_amount() >= 1;
}

/* Returns true when the geometry set has a volume component that has a volume. */
bool GeometrySet::has_volume() const
{
  const VolumeComponent *component = this->get_component_for_read<VolumeComponent>();
  return component != nullptr && component->has_volume();
}

/* Create a new geometry set that only contains the given mesh. */
GeometrySet GeometrySet::create_with_mesh(Mesh *mesh, GeometryOwnershipType ownership)
{
  GeometrySet geometry_set;
  MeshComponent &component = geometry_set.get_component_for_write<MeshComponent>();
  component.replace(mesh, ownership);
  return geometry_set;
}

/* Create a new geometry set that only contains the given point cloud. */
GeometrySet GeometrySet::create_with_pointcloud(PointCloud *pointcloud,
                                                GeometryOwnershipType ownership)
{
  GeometrySet geometry_set;
  PointCloudComponent &component = geometry_set.get_component_for_write<PointCloudComponent>();
  component.replace(pointcloud, ownership);
  return geometry_set;
}

/* Clear the existing mesh and replace it with the given one. */
void GeometrySet::replace_mesh(Mesh *mesh, GeometryOwnershipType ownership)
{
  MeshComponent &component = this->get_component_for_write<MeshComponent>();
  component.replace(mesh, ownership);
}

/* Clear the existing point cloud and replace with the given one. */
void GeometrySet::replace_pointcloud(PointCloud *pointcloud, GeometryOwnershipType ownership)
{
  PointCloudComponent &pointcloud_component = this->get_component_for_write<PointCloudComponent>();
  pointcloud_component.replace(pointcloud, ownership);
}

/* Returns a mutable mesh or null. No ownership is transferred. */
Mesh *GeometrySet::get_mesh_for_write()
{
  MeshComponent &component = this->get_component_for_write<MeshComponent>();
  return component.get_for_write();
}

/* Returns a mutable point cloud or null. No ownership is transferred. */
PointCloud *GeometrySet::get_pointcloud_for_write()
{
  PointCloudComponent &component = this->get_component_for_write<PointCloudComponent>();
  return component.get_for_write();
}

/* Returns a mutable volume or null. No ownership is transferred. */
Volume *GeometrySet::get_volume_for_write()
{
  VolumeComponent &component = this->get_component_for_write<VolumeComponent>();
  return component.get_for_write();
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Mesh Component
 * \{ */

MeshComponent::MeshComponent() : GeometryComponent(GeometryComponentType::Mesh)
{
}

MeshComponent::~MeshComponent()
{
  this->clear();
}

GeometryComponent *MeshComponent::copy() const
{
  MeshComponent *new_component = new MeshComponent();
  if (mesh_ != nullptr) {
    new_component->mesh_ = BKE_mesh_copy_for_eval(mesh_, false);
    new_component->ownership_ = GeometryOwnershipType::Owned;
    new_component->vertex_group_names_ = blender::Map(vertex_group_names_);
  }
  return new_component;
}

void MeshComponent::clear()
{
  BLI_assert(this->is_mutable());
  if (mesh_ != nullptr) {
    if (ownership_ == GeometryOwnershipType::Owned) {
      BKE_id_free(nullptr, mesh_);
    }
    mesh_ = nullptr;
  }
  vertex_group_names_.clear();
}

bool MeshComponent::has_mesh() const
{
  return mesh_ != nullptr;
}

/* Clear the component and replace it with the new mesh. */
void MeshComponent::replace(Mesh *mesh, GeometryOwnershipType ownership)
{
  BLI_assert(this->is_mutable());
  this->clear();
  mesh_ = mesh;
  ownership_ = ownership;
}

/* This function exists for the same reason as #vertex_group_names_. Non-nodes modifiers need to
 * be able to replace the mesh data without losing the vertex group names, which may have come
 * from another object. */
void MeshComponent::replace_mesh_but_keep_vertex_group_names(Mesh *mesh,
                                                             GeometryOwnershipType ownership)
{
  BLI_assert(this->is_mutable());
  if (mesh_ != nullptr) {
    if (ownership_ == GeometryOwnershipType::Owned) {
      BKE_id_free(nullptr, mesh_);
    }
    mesh_ = nullptr;
  }
  mesh_ = mesh;
  ownership_ = ownership;
}

/* Return the mesh and clear the component. The caller takes over responsibility for freeing the
 * mesh (if the component was responsible before). */
Mesh *MeshComponent::release()
{
  BLI_assert(this->is_mutable());
  Mesh *mesh = mesh_;
  mesh_ = nullptr;
  return mesh;
}

void MeshComponent::copy_vertex_group_names_from_object(const Object &object)
{
  BLI_assert(this->is_mutable());
  vertex_group_names_.clear();
  int index = 0;
  LISTBASE_FOREACH (const bDeformGroup *, group, &object.defbase) {
    vertex_group_names_.add(group->name, index);
    index++;
  }
}

const blender::Map<std::string, int> &MeshComponent::vertex_group_names() const
{
  return vertex_group_names_;
}

/* This is only exposed for the internal attribute API. */
blender::Map<std::string, int> &MeshComponent::vertex_group_names()
{
  return vertex_group_names_;
}

/* Get the mesh from this component. This method can be used by multiple threads at the same
 * time. Therefore, the returned mesh should not be modified. No ownership is transferred. */
const Mesh *MeshComponent::get_for_read() const
{
  return mesh_;
}

/* Get the mesh from this component. This method can only be used when the component is mutable,
 * i.e. it is not shared. The returned mesh can be modified. No ownership is transferred. */
Mesh *MeshComponent::get_for_write()
{
  BLI_assert(this->is_mutable());
  if (ownership_ == GeometryOwnershipType::ReadOnly) {
    mesh_ = BKE_mesh_copy_for_eval(mesh_, false);
    ownership_ = GeometryOwnershipType::Owned;
  }
  return mesh_;
}

bool MeshComponent::is_empty() const
{
  return mesh_ == nullptr;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Pointcloud Component
 * \{ */

PointCloudComponent::PointCloudComponent() : GeometryComponent(GeometryComponentType::PointCloud)
{
}

PointCloudComponent::~PointCloudComponent()
{
  this->clear();
}

GeometryComponent *PointCloudComponent::copy() const
{
  PointCloudComponent *new_component = new PointCloudComponent();
  if (pointcloud_ != nullptr) {
    new_component->pointcloud_ = BKE_pointcloud_copy_for_eval(pointcloud_, false);
    new_component->ownership_ = GeometryOwnershipType::Owned;
  }
  return new_component;
}

void PointCloudComponent::clear()
{
  BLI_assert(this->is_mutable());
  if (pointcloud_ != nullptr) {
    if (ownership_ == GeometryOwnershipType::Owned) {
      BKE_id_free(nullptr, pointcloud_);
    }
    pointcloud_ = nullptr;
  }
}

bool PointCloudComponent::has_pointcloud() const
{
  return pointcloud_ != nullptr;
}

/* Clear the component and replace it with the new point cloud. */
void PointCloudComponent::replace(PointCloud *pointcloud, GeometryOwnershipType ownership)
{
  BLI_assert(this->is_mutable());
  this->clear();
  pointcloud_ = pointcloud;
  ownership_ = ownership;
}

/* Return the point cloud and clear the component. The caller takes over responsibility for freeing
 * the point cloud (if the component was responsible before). */
PointCloud *PointCloudComponent::release()
{
  BLI_assert(this->is_mutable());
  PointCloud *pointcloud = pointcloud_;
  pointcloud_ = nullptr;
  return pointcloud;
}

/* Get the point cloud from this component. This method can be used by multiple threads at the same
 * time. Therefore, the returned point cloud should not be modified. No ownership is transferred.
 */
const PointCloud *PointCloudComponent::get_for_read() const
{
  return pointcloud_;
}

/* Get the point cloud from this component. This method can only be used when the component is
 * mutable, i.e. it is not shared. The returned point cloud can be modified. No ownership is
 * transferred. */
PointCloud *PointCloudComponent::get_for_write()
{
  BLI_assert(this->is_mutable());
  if (ownership_ == GeometryOwnershipType::ReadOnly) {
    pointcloud_ = BKE_pointcloud_copy_for_eval(pointcloud_, false);
    ownership_ = GeometryOwnershipType::Owned;
  }
  return pointcloud_;
}

bool PointCloudComponent::is_empty() const
{
  return pointcloud_ == nullptr;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Instances Component
 * \{ */

InstancesComponent::InstancesComponent() : GeometryComponent(GeometryComponentType::Instances)
{
}

GeometryComponent *InstancesComponent::copy() const
{
  InstancesComponent *new_component = new InstancesComponent();
  new_component->transforms_ = transforms_;
  new_component->instanced_data_ = instanced_data_;
  return new_component;
}

void InstancesComponent::clear()
{
  instanced_data_.clear();
  transforms_.clear();
}

void InstancesComponent::add_instance(Object *object, float4x4 transform, const int id)
{
  InstancedData data;
  data.type = INSTANCE_DATA_TYPE_OBJECT;
  data.data.object = object;
  this->add_instance(data, transform, id);
}

void InstancesComponent::add_instance(Collection *collection, float4x4 transform, const int id)
{
  InstancedData data;
  data.type = INSTANCE_DATA_TYPE_COLLECTION;
  data.data.collection = collection;
  this->add_instance(data, transform, id);
}

void InstancesComponent::add_instance(InstancedData data, float4x4 transform, const int id)
{
  instanced_data_.append(data);
  transforms_.append(transform);
  ids_.append(id);
}

Span<InstancedData> InstancesComponent::instanced_data() const
{
  return instanced_data_;
}

Span<float4x4> InstancesComponent::transforms() const
{
  return transforms_;
}

Span<int> InstancesComponent::ids() const
{
  return ids_;
}

MutableSpan<float4x4> InstancesComponent::transforms()
{
  return transforms_;
}

int InstancesComponent::instances_amount() const
{
  const int size = instanced_data_.size();
  BLI_assert(transforms_.size() == size);
  return size;
}

bool InstancesComponent::is_empty() const
{
  return transforms_.size() == 0;
}

/**
 * \note This doesn't extract instances from the "dupli" system for non-geometry-nodes instances.
 */
static GeometrySet object_get_geometry_set_for_read(const Object &object)
{
  /* Objects evaluated with a nodes modifier will have a geometry set already. */
  if (object.runtime.geometry_set_eval != nullptr) {
    return *object.runtime.geometry_set_eval;
  }

  /* Otherwise, construct a new geometry set with the component based on the object type. */
  GeometrySet new_geometry_set;

  if (object.type == OB_MESH) {
    Mesh *mesh = BKE_modifier_get_evaluated_mesh_from_evaluated_object(
        &const_cast<Object &>(object), false);

    if (mesh != nullptr) {
      BKE_mesh_wrapper_ensure_mdata(mesh);

      MeshComponent &mesh_component = new_geometry_set.get_component_for_write<MeshComponent>();
      mesh_component.replace(mesh, GeometryOwnershipType::ReadOnly);
      mesh_component.copy_vertex_group_names_from_object(object);
    }
  }

  /* TODO: Cover the case of pointclouds without modifiers-- they may not be covered by the
   * #geometry_set_eval case above. */

  /* TODO: Add volume support. */

  /* Return by value since there is not always an existing geometry set owned elsewhere to use. */
  return new_geometry_set;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Geometry Set Gather Recursive Instances
 * \{ */

static void geometry_set_collect_recursive(const GeometrySet &geometry_set,
                                           const float4x4 &transform,
                                           Vector<GeometryInstanceGroup> &r_sets);

static void geometry_set_collect_recursive_collection(const Collection &collection,
                                                      const float4x4 &transform,
                                                      Vector<GeometryInstanceGroup> &r_sets);

static void geometry_set_collect_recursive_collection_instance(
    const Collection &collection, const float4x4 &transform, Vector<GeometryInstanceGroup> &r_sets)
{
  float4x4 offset_matrix;
  unit_m4(offset_matrix.values);
  sub_v3_v3(offset_matrix.values[3], collection.instance_offset);
  const float4x4 instance_transform = transform * offset_matrix;
  geometry_set_collect_recursive_collection(collection, instance_transform, r_sets);
}

static void geometry_set_collect_recursive_object(const Object &object,
                                                  const float4x4 &transform,
                                                  Vector<GeometryInstanceGroup> &r_sets)
{
  GeometrySet instance_geometry_set = object_get_geometry_set_for_read(object);
  geometry_set_collect_recursive(instance_geometry_set, transform, r_sets);

  if (object.type == OB_EMPTY) {
    const Collection *collection_instance = object.instance_collection;
    if (collection_instance != nullptr) {
      geometry_set_collect_recursive_collection_instance(*collection_instance, transform, r_sets);
    }
  }
}

static void geometry_set_collect_recursive_collection(const Collection &collection,
                                                      const float4x4 &transform,
                                                      Vector<GeometryInstanceGroup> &r_sets)
{
  LISTBASE_FOREACH (const CollectionObject *, collection_object, &collection.gobject) {
    BLI_assert(collection_object->ob != nullptr);
    const Object &object = *collection_object->ob;
    const float4x4 object_transform = transform * object.obmat;
    geometry_set_collect_recursive_object(object, object_transform, r_sets);
  }
  LISTBASE_FOREACH (const CollectionChild *, collection_child, &collection.children) {
    BLI_assert(collection_child->collection != nullptr);
    const Collection &collection = *collection_child->collection;
    geometry_set_collect_recursive_collection(collection, transform, r_sets);
  }
}

static void geometry_set_collect_recursive(const GeometrySet &geometry_set,
                                           const float4x4 &transform,
                                           Vector<GeometryInstanceGroup> &r_sets)
{
  r_sets.append({geometry_set, {transform}});

  if (geometry_set.has_instances()) {
    const InstancesComponent &instances_component =
        *geometry_set.get_component_for_read<InstancesComponent>();

    Span<float4x4> transforms = instances_component.transforms();
    Span<InstancedData> instances = instances_component.instanced_data();
    for (const int i : instances.index_range()) {
      const InstancedData &data = instances[i];
      const float4x4 instance_transform = transform * transforms[i];

      if (data.type == INSTANCE_DATA_TYPE_OBJECT) {
        BLI_assert(data.data.object != nullptr);
        const Object &object = *data.data.object;
        geometry_set_collect_recursive_object(object, instance_transform, r_sets);
      }
      else if (data.type == INSTANCE_DATA_TYPE_COLLECTION) {
        BLI_assert(data.data.collection != nullptr);
        const Collection &collection = *data.data.collection;
        geometry_set_collect_recursive_collection_instance(collection, instance_transform, r_sets);
      }
    }
  }
}

/**
 * Return flattened vector of the geometry component's recursive instances. I.e. all collection
 * instances and object instances will be expanded into the instances of their geometry components.
 * Even the instances in those geometry components' will be included.
 *
 * \note For convenience (to avoid duplication in the caller), the returned vector also contains
 * the argument geometry set.
 *
 * \note This doesn't extract instances from the "dupli" system for non-geometry-nodes instances.
 */
Vector<GeometryInstanceGroup> BKE_geometry_set_gather_instances(const GeometrySet &geometry_set)
{
  Vector<GeometryInstanceGroup> result_vector;

  float4x4 unit_transform;
  unit_m4(unit_transform.values);

  geometry_set_collect_recursive(geometry_set, unit_transform, result_vector);

  return result_vector;
}

static blender::Array<int> generate_unique_instance_ids(Span<int> original_ids)
{
  using namespace blender;
  Array<int> unique_ids(original_ids.size());

  Set<int> used_unique_ids;
  used_unique_ids.reserve(original_ids.size());
  Vector<int> instances_with_id_collision;
  for (const int instance_index : original_ids.index_range()) {
    const int original_id = original_ids[instance_index];
    if (used_unique_ids.add(original_id)) {
      /* The original id has not been used by another instance yet. */
      unique_ids[instance_index] = original_id;
    }
    else {
      /* The original id of this instance collided with a previous instance, it needs to be looked
       * at again in a second pass. Don't generate a new random id here, because this might collide
       * with other existing ids. */
      instances_with_id_collision.append(instance_index);
    }
  }

  Map<int, RandomNumberGenerator> generator_by_original_id;
  for (const int instance_index : instances_with_id_collision) {
    const int original_id = original_ids[instance_index];
    RandomNumberGenerator &rng = generator_by_original_id.lookup_or_add_cb(original_id, [&]() {
      RandomNumberGenerator rng;
      rng.seed_random(original_id);
      return rng;
    });

    const int max_iteration = 100;
    for (int iteration = 0;; iteration++) {
      /* Try generating random numbers until an unused one has been found. */
      const int random_id = rng.get_int32();
      if (used_unique_ids.add(random_id)) {
        /* This random id is not used by another instance. */
        unique_ids[instance_index] = random_id;
        break;
      }
      if (iteration == max_iteration) {
        /* It seems to be very unlikely that we ever run into this case (assuming there are less
         * than 2^30 instances). However, if that happens, it's better to use an id that is not
         * unique than to be stuck in an infinite loop. */
        unique_ids[instance_index] = original_id;
        break;
      }
    }
  }

  return unique_ids;
}

blender::Span<int> InstancesComponent::almost_unique_ids() const
{
  std::lock_guard lock(almost_unique_ids_mutex_);
  if (almost_unique_ids_.size() != ids_.size()) {
    almost_unique_ids_ = generate_unique_instance_ids(ids_);
  }
  return almost_unique_ids_;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name Volume Component
 * \{ */

VolumeComponent::VolumeComponent() : GeometryComponent(GeometryComponentType::Volume)
{
}

VolumeComponent::~VolumeComponent()
{
  this->clear();
}

GeometryComponent *VolumeComponent::copy() const
{
  VolumeComponent *new_component = new VolumeComponent();
  if (volume_ != nullptr) {
    new_component->volume_ = BKE_volume_copy_for_eval(volume_, false);
    new_component->ownership_ = GeometryOwnershipType::Owned;
  }
  return new_component;
}

void VolumeComponent::clear()
{
  BLI_assert(this->is_mutable());
  if (volume_ != nullptr) {
    if (ownership_ == GeometryOwnershipType::Owned) {
      BKE_id_free(nullptr, volume_);
    }
    volume_ = nullptr;
  }
}

bool VolumeComponent::has_volume() const
{
  return volume_ != nullptr;
}

/* Clear the component and replace it with the new volume. */
void VolumeComponent::replace(Volume *volume, GeometryOwnershipType ownership)
{
  BLI_assert(this->is_mutable());
  this->clear();
  volume_ = volume;
  ownership_ = ownership;
}

/* Return the volume and clear the component. The caller takes over responsibility for freeing the
 * volume (if the component was responsible before). */
Volume *VolumeComponent::release()
{
  BLI_assert(this->is_mutable());
  Volume *volume = volume_;
  volume_ = nullptr;
  return volume;
}

/* Get the volume from this component. This method can be used by multiple threads at the same
 * time. Therefore, the returned volume should not be modified. No ownership is transferred. */
const Volume *VolumeComponent::get_for_read() const
{
  return volume_;
}

/* Get the volume from this component. This method can only be used when the component is mutable,
 * i.e. it is not shared. The returned volume can be modified. No ownership is transferred. */
Volume *VolumeComponent::get_for_write()
{
  BLI_assert(this->is_mutable());
  if (ownership_ == GeometryOwnershipType::ReadOnly) {
    volume_ = BKE_volume_copy_for_eval(volume_, false);
    ownership_ = GeometryOwnershipType::Owned;
  }
  return volume_;
}

/** \} */

/* -------------------------------------------------------------------- */
/** \name C API
 * \{ */

void BKE_geometry_set_free(GeometrySet *geometry_set)
{
  delete geometry_set;
}

bool BKE_geometry_set_has_instances(const GeometrySet *geometry_set)
{
  return geometry_set->get_component_for_read<InstancesComponent>() != nullptr;
}

int BKE_geometry_set_instances(const GeometrySet *geometry_set,
                               float (**r_transforms)[4][4],
                               const int **r_almost_unique_ids,
                               InstancedData **r_instanced_data)
{
  const InstancesComponent *component = geometry_set->get_component_for_read<InstancesComponent>();
  if (component == nullptr) {
    return 0;
  }
  *r_transforms = (float(*)[4][4])component->transforms().data();
  *r_instanced_data = (InstancedData *)component->instanced_data().data();
  *r_almost_unique_ids = (const int *)component->almost_unique_ids().data();
  return component->instances_amount();
}

/** \} */
